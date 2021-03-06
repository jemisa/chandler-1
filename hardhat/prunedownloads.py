#!/usr/bin/env python

# This should be run once a day on a machine hosting chandler continuous
# builds. The job of this script is to prune excess directories/old
# downloads.
#
# The default policy is as follows:
# - keep all builds from the last 48 hours
# - keep one build per day for the past 30 days
# - keep the latest build
# - delete all others
#
# We assume directory structure as follows:
#
# + absolute start directory
#   + (*-osx | *-linux | *-win)
#     + YYYYMMDDHHMMSS
#
# We delete all YYYYMMDDHHMMSS directories that don't match our policy.

shortPolicyHours = 48
longPolicyDays   = 30
smtpServer       = 'mail.osafoundation.org'
downloadsServer  = 'builds'
fromAddr         = 'builds'
toAddr           = 'bear'
defaultDomain    = 'osafoundation.org'
startDir         = '/home/builder/www/docs/chandler/continuous'
tboxDirGlob      = ['*-win', '*-osx', '*-linux']

import datetime, time, smtplib, os, glob


class mylog:
    def __init__(self):
        self.data = ''

    def __str__(self):
        return self.data
    
    def write(self, data):
        self.data += data


def rmdirRecursive(dir):
    """
    Recursively remove a directory.
    Parameters:
        dir: directory path
    Returns:
        nothing
    """

    if os.path.islink(dir):
        os.remove(dir)
        return

    for name in os.listdir(dir):
        full_name = os.path.join(dir, name)
        # on Windows, if we don't have write permission we can't remove
        # the file/directory either, so turn that on
        if os.name == 'nt':
            if not os.access(full_name, os.W_OK):
                os.chmod(full_name, 0600)
        if os.path.isdir(full_name):
            rmdirRecursive(full_name)
        else:
            # print "removing file", full_name
            os.remove(full_name)
    os.rmdir(dir)


def prune():
    global startDir

    nowDT = datetime.datetime.now()
    tooOld = nowDT - datetime.timedelta(days=longPolicyDays)
    tooNew = nowDT - datetime.timedelta(hours=longPolicyDays)

    tooOldStr = tooOld.strftime("%Y%m%d%H%M%S")
    tooNewStr = tooNew.strftime("%Y%m%d%H%M%S")
    
    os.chdir(startDir)

    # get directories where tbox clients rsync their distributions
    topdirs = []
    for dirGlob in tboxDirGlob:
        topdirs += glob.glob(dirGlob)

    # process topdirs
    for dir in topdirs:
        os.chdir(startDir)

        if not os.path.isdir(dir):
            continue

        os.chdir(os.path.join(startDir, dir))
    
        # now the real pruning happens here
        betweenDays = {}
        archivedirs = glob.glob('[0-9]*')
        for archive in archivedirs[:-1]: # [:-1] means 'leave latest'
            if len(archive) != 14 or not os.path.isdir(archive):
                continue 

            if archive < tooOldStr:
                print 'delete ', os.path.join(startDir, dir, archive)
                rmdirRecursive(archive)
                continue
            
            if archive > tooNewStr:
                print 'leave ', os.path.join(startDir, dir, archive)
                continue

            # Now all we have left are those in-betweens...

            day = archive[:8]
            if betweenDays.has_key(day):
                print 'delete ', os.path.join(startDir, dir, archive)
                rmdirRecursive(archive)
                continue
            
            betweenDays[day] = 1
            print 'leave ', os.path.join(startDir, dir, archive)


def main():
    global shortPolicyHours, longPolicyDays, smtpServer, downloadsServer
    global fromAddr, toAddr

    fromAddr += '@' + defaultDomain
    toAddr   += '@' + defaultDomain
    
    try:
        prune()
    except Exception, e:
        import traceback
        log = mylog()
        traceback.print_exc(file=log)
        SendMail(fromAddr, toAddr, downloadsServer,  log)


def SendMail(fromAddr, toAddr, serverName, log):
    global smtpServer
    
    subject  = "[prunedownloads] problem from " + serverName
    msg      = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromAddr, toAddr, subject))
    msg      += str(log)

    print msg

    server = smtplib.SMTP(smtpServer)
    server.sendmail(fromAddr, toAddr, msg)
    server.quit()


main()
