__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2004 Open Source Applications Foundation"
__license__ = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

import application.Globals as Globals
from osaf.framework.blocks.Views import View
from osaf.framework.notifications.Notification import Notification
import wx
import os
import application.dialogs.AccountPreferences
import application.dialogs.Util
import osaf.contentmodel.mail.Mail as Mail
from application.SplashScreen import SplashScreen
from application.Parcel import Manager as ParcelManager
from osaf.mail.imap import IMAPDownloader
import osaf.contentmodel.contacts.Contacts as Contacts
import osaf.framework.utils.imports.OutlookContacts as OutlookContacts
import osaf.contentmodel.tests.GenerateItems as GenerateItems
from repository.persistence.RepositoryError import VersionConflictError
import repository.util.UUID as UUID
import osaf.framework.sharing.Sharing as Sharing
import repository.query.Query as Query
import repository.item.Query as ItemQuery
import osaf.mail.sharing as MailSharing
import osaf.framework.webdav.Dav as Dav


class MainView(View):
    """
      Main Chandler view contains event handlers for Chandler
    """
    def onNULLEvent (self, notification):
        """ The NULL Event handler """
        pass

    def onNULLEventUpdateUI (self, notification):
        """ The NULL Event is always disabled """
        notification.data ['Enable'] = False

    def onQuitEvent (self, notification):
        Globals.wxApplication.mainFrame.Close ()

    def onUndoEventUpdateUI (self, notification):
        notification.data ['Text'] = "Can't Undo\tCtrl+Z"
        notification.data ['Enable'] = False

    def onRedoEventUpdateUI (self, notification):
        notification.data ['Enable'] = False

    def onCutEventUpdateUI (self, notification):
        notification.data ['Enable'] = False

    def onCopyEventUpdateUI (self, notification):
        notification.data ['Enable'] = False

    def onPasteEventUpdateUI (self, notification):
        notification.data ['Enable'] = False

    def onPreferencesEventUpdateUI (self, notification):
        notification.data ['Enable'] = False

    def onSharingSubscribeToCollectionEvent(self, notification):
        # Triggered from "Tests | Subscribe to collection..."
        Sharing.manualSubscribeToCollection()

    def onEditAccountPreferencesEvent (self, notification):
        # Triggered from "File | Prefs | Accounts..."
        Mail.EmailAddress.captureCurrentMeEmailAddress()
        application.dialogs.AccountPreferences.ShowAccountPreferencesDialog(Globals.wxApplication.mainFrame)
        # if the "me" address was changed by editing, we'll start using a new one.
        Mail.EmailAddress.releaseCurrentMeEmailAddress()

    def onEditMailAccountEvent (self, notification):
        # @@@ Deprecated, replaced by onEditAccountPreferencesEvent, above

        account = \
         Globals.repository.findPath('//parcels/osaf/mail/IMAPAccountOne')
        if application.dialogs.Util.promptForItemValues(
         Globals.wxApplication.mainFrame,
         "IMAP Account",
         account,
         [
           { "attr":"host", "label":"IMAP Server" },
           { "attr":"username", "label":"Username" },
           { "attr":"password", "label":"Password", "password":True },
         ]
        ):
            try:
                Globals.repository.commit()
            except VersionConflictError, e:
                # A first experiment with resolving conflicts.  Not sure
                # yet where the logic for handling this should live.  Could
                # be here, could be handled by the conflicting item itself(?).

                # Retrieve the conflicting item
                conflict = e.getItem()
                itemPath = conflict.itsPath
                host = conflict.host
                username = conflict.username
                password = conflict.password
                print "Got a conflict with item:", itemPath
                # The conflict item has *our* values in it; to see the
                # values that were committed by the other thread, we need
                # to cancel our transaction, commit, and refetch the item.
                Globals.repository.cancel()
                # Get the latest items committed from other threads
                Globals.repository.commit()
                # Refetch item
                account = Globals.repository.findPath(itemPath)
                # To resolve this conflict we're going to simply reapply the 
                # values that were set in the dialog box.
                account.host = host
                account.username = username
                account.password = password
                Globals.repository.commit()
                # Note: this commit, too, could get a conflict I suppose, so
                # do we need to put this sort of conflict resolution in a loop?
                print "Conflict resolved"


    def onGetNewMailEvent (self, notification):
        account = \
         Globals.repository.findPath('//parcels/osaf/mail/IMAPAccountOne')
        IMAPDownloader (account).getMail()

    def onNewEvent (self, notification):
        # create a new content item
        event = notification.event
        itemName = 'Anonymous'+str(UUID.UUID())
        newItem = event.kindParameter.newItem (itemName, self)
        newItem.InitOutgoingAttributes ()
        Globals.repository.commit()

        # lookup our Request Select Events
        rootPath = '//parcels/osaf/framework/blocks/Events/'
        requestSelectSidebarItem = Globals.repository.findPath \
                                (rootPath + 'RequestSelectSidebarItem')
        requestSelectItem = Globals.repository.findPath \
                                   (rootPath + 'RequestSelectItem')

        # Tell the sidebar we want to go to the 'All' box
        args = {}
        args['itemName'] = 'AllTableView'
        contactKind = Contacts.ContactsParcel.getContactKind ()
        if newItem.isItemOf (contactKind):
            args['itemName'] = 'ContactTableView'
        self.Post(requestSelectSidebarItem, args)

        # Tell the ActiveView to select our new item
        args = {}
        args['item'] = newItem
        self.Post(requestSelectItem, args)

    def onNewEventUpdateUI (self, notification):
        notification.data ['Enable'] = True

    # Test Methods

    def onGenerateContentItemsEvent(self, notification): 
        GenerateItems.GenerateNotes(2) 
        GenerateItems.generateCalendarEventItems(2, 30) 
        GenerateItems.GenerateContacts(2) 
        Globals.repository.commit() 

    def onGenerateCalendarEventItemsEvent(self, notification):
        GenerateItems.generateCalendarEventItems(10, 30)
        Globals.repository.commit()

    def onGenerateContactsEvent(self, notification):
        GenerateItems.GenerateContacts(10)
        Globals.repository.commit()

    def onImportContactsEvent(self, notification):
        x=OutlookContacts.OutlookContacts().processFile()

    def onGenerateNotesEvent(self, notification):
        GenerateItems.GenerateNotes(10)
        Globals.repository.commit()

    def onCheckRepositoryEvent(self, notification):

        repository = Globals.repository
        repository.logger.info('Checking repository...')
        if repository.check():
            repository.logger.info('Check completed successfully')
        else:
            repository.logger.info('Check completed with errors')

    def onShowPyCrustEvent(self, notification):
        Globals.wxApplication.ShowDebuggerWindow()

    def onReloadParcelsEvent(self, notification):
        ParcelManager.getManager().loadParcels()
        self.rerender ()

    def onCommitRepositoryEvent(self, notification):
        Globals.repository.commit()

    def onAboutChandlerEvent(self, notification):
        """
          Show the splash screen in response to the about command
        """
        pageLocation = os.path.join ('application', 'welcome.html')
        splash = SplashScreen(None, _("About Chandler"), 
                              pageLocation, False, False)
        splash.Show(True)

    def getSidebarSelectedCollection (self):
        """
          Return the sidebar's selected item collection.

          The sidebar is a table, whose contents is a collection.
        The selection is a table (one of the splitters), 
        whose contents is a collection.
        """
        sidebarPath = '//parcels/osaf/views/main/Sidebar'
        sidebar = Globals.repository.findPath (sidebarPath)
        selectedBlock = sidebar.selection
        assert selectedBlock, "No selected block in the Sidebar"
        try:
            selectionContents = selectedBlock.contents
        except AttributeError:
            selectionContents = None
        return selectionContents

    def onShareCollectionEvent (self, notification):
        # Triggered from "Test | Share collection..."
        collection = self.getSidebarSelectedCollection ()
        if collection is not None:
            Sharing.manualPublishCollection(collection)

    def onShareCollectionEventUpdateUI (self, notification):
        """
        Update the menu to reflect the selected collection name
        """
        # Only enable it user has set their webdav account up
        if not self.webDAVAccountIsSetup ():
            notification.data ['Enable'] = False
            return

        collection = self.getSidebarSelectedCollection ()
        notification.data ['Enable'] = collection is not None
        if collection:
            menuTitle = 'Share collection "%s"' \
                    % collection.displayName
        else:
            menuTitle = 'Share a collection'
        notification.data ['Text'] = menuTitle

    def onSyncCollectionEvent (self, notification):
        # Triggered from "Test | Sync collection..."
        collection = self.getSidebarSelectedCollection ()
        if collection is not None:
            Sharing.syncCollection(collection)

    def onSyncCollectionEventUpdateUI (self, notification):
        """
        Update the menu to reflect the selected collection name
        """
        collection = self.getSidebarSelectedCollection ()
        if collection is not None:
            menuTitle = 'Sync collection "%s"' % collection.displayName
            if Sharing.isShared(collection):
                notification.data['Enable'] = True
            else:
                notification.data['Enable'] = False
        else:
            notification.data['Enable'] = False
            menuTitle = 'Sync a collection'
        notification.data ['Text'] = menuTitle

    def onSyncWebDAVEvent (self, notification):
        """
          Synchronize WebDAV sharing.
        """
        # find all the shared collections and sync them.
        self.setStatusText ("checking shared collections")
        collections = self.sharedWebDAVCollections ()
        if len (collections) == 0:
            self.setStatusText ("No shared collections found")
            return
        for collection in collections:
            self.setStatusText ("synchronizing %s" % collection)
            Sharing.syncCollection(collection)

        # synch mail
        self.setStatusText ("Sharing synchronized.")

    def onSyncWebDAVEventUpdateUI (self, notification):
        accountOK = self.webDAVAccountIsSetup ()
        sharedCollections = self.sharedWebDAVCollections ()
        enable = accountOK and len (sharedCollections) > 0
        notification.data ['Enable'] = enable
        # DLDTBD set up the help string to let the user know why it's disabled

    def webDAVAccountIsSetup (self):
        # return True iff the webDAV account is set up
        return Sharing.getWebDavPath() != None
        
    def sharedWebDAVCollections (self):
        # return the list of all the shared collections
        # DLDTBD - use new query, once it can handle method calls, or when our item.isShared
        #  attribute is correctly set.
        UseNewQuery = False
        if UseNewQuery:
            qString = u"for i in '//parcels/osaf/contentmodel/ItemCollection' where len (i.sharedURL) > 0"
            collQuery = Query.Query (Globals.repository, qString)
            collQuery.recursive = False
            collections = []
            for item in collQuery:
                collections.append (item)
        else:
            itemCollectionKind = Globals.repository.findPath("//parcels/osaf/contentmodel/ItemCollection")
            allCollections = ItemQuery.KindQuery().run([itemCollectionKind])
            collections = []
            for collection in allCollections:
                if Sharing.isShared (collection):
                    collections.append (collection)
        return collections

    def onSyncAllEvent (self, notification):
        """
          Synchronize Mail and all sharing.
        """
        # find all the shared collections and sync them.
        self.onSyncWebDAVEvent (notification)

        # synch mail
        self.setStatusText ("Getting new Mail")
        self.onGetNewMailEvent (notification)

    def onShareOrManageEvent (self, notification):
        """
          Share the collection selected in the Sidebar. 
        If the current collection is already shared, then manage the collection.
        In either case, the real work here is to tell the summary
        view to deselect, and the detail view that the selection has
        changed to the entire summary view's collection.
        """
        # lookup the Request Select Event
        rootPath = '//parcels/osaf/framework/blocks/Events/'
        requestSelectItem = Globals.repository.findPath \
                                   (rootPath + 'RequestSelectItem')

        # Tell the ActiveView to select the collection
        # It will pass the collection on to the Detail View.
        args = {}
        args['item'] = None
        args['collection'] = True
        self.Post(requestSelectItem, args)

    def onShareOrManageEventUpdateUI (self, notification):
        """
        Update the menu to reflect the selected collection name
        """
        collection = self.getSidebarSelectedCollection ()
        accountOK = self.webDAVAccountIsSetup ()
        if accountOK and collection is not None:
            notification.data['Enable'] = True
            if Sharing.isShared (collection):
                menuTitle = 'Manage collection "%s"' % collection.displayName
            else:
                menuTitle = 'Share collection "%s"' % collection.displayName
        else:
            notification.data['Enable'] = False
            menuTitle = 'Share a collection'
        notification.data ['Text'] = menuTitle

    def setStatusText (self, statusMessage):
        Globals.wxApplication.mainFrame.SetStatusText (statusMessage)

    def onMessageMainViewEvent (self, notification):
        """
          Handler for general message to call one of my methods.
        Used by ContentModel when it wants to call a method here,
        e.g. setStatusText.
        """
        # unpack the arguments
        data = notification.data
        args = data['__args']
        keys = data['__keys']
        methodName = data['__methodName']
        # look up the method by name
        try:
            member = getattr (type(self), methodName)
        except AttributeError:
            return
        # call the method with params
        member (self, *args, **keys)

    def SharingInvitees (self, itemCollection):
        # return the list of sharing invitees
        inviteeStringsList = []
        try:
            invitees = itemCollection.sharees
        except AttributeError:
            invitees = []
        for entity in invitees:
            inviteeStringsList.append (entity.emailAddress)
        return inviteeStringsList

    def SharingURL (self, itemCollection):
        # Return the url used to share the itemCollection.
        if Sharing.isShared (itemCollection):
            url = str (itemCollection.sharedURL)
        else:
            path = Sharing.getWebDavPath()
            if path:
                url = "%s/%s" % (path, itemCollection.itsUUID)
            else:
                self.setStatusText ("You need to set up the server and path in the account dialog!")
                return
            url = url.encode ('utf-8')
        return url

    def SendSharingInvitations (self, itemCollection, url):
        inviteeStringsList = self.SharingInvitees (itemCollection)
        MailSharing.sendInvitation(url, itemCollection.displayName, inviteeStringsList)

    def onResendSharingInvitations (self, notification):
        """
          Resend the sharing invitations for the selected collection.
        This is a Test menu item handler.
        """
        itemCollection = self.getSidebarSelectedCollection ()
        url = self.SharingURL (itemCollection)
        self.SendSharingInvitations (itemCollection, url)

    def onResendSharingInvitationsUpdateUI (self, notification):
        collection = self.getSidebarSelectedCollection ()
        isShared = Sharing.isShared (collection)
        notification.data ['Enable'] = isShared

    def ShareCollection (self, itemCollection):
        # put a "committing" message into the status bar
        self.setStatusText ('Committing changes...')

        # commit changes, since we'll be switching to Twisted thread
        Globals.repository.commit()

        # show status
        self.setStatusText ("Sharing collection %s" % itemCollection.displayName)
    
        # check that it's not already shared, and we have the sharing account set up.
        url = self.SharingURL (itemCollection)

        # build list of invitees.
        if len (self.SharingInvitees (itemCollection)) == 0:
            self.setStatusText ("No sharees!")
            return

        # change the name to include "Shared"
        if not "Shared" in itemCollection.displayName:
            itemCollection.displayName = "%s (Shared)" % itemCollection.displayName

        # Sync the collection with WebDAV
        self.setStatusText ("accessing WebDAV server")
        Dav.DAV(url).put(itemCollection)

        # Send out sharing invites
        inviteeStringsList = self.SharingInvitees (itemCollection)
        self.setStatusText ("inviting %s" % inviteeStringsList)
        self.SendSharingInvitations (itemCollection, url)

        # set the isShared attribute on the collection, so queries can find them
        itemCollection.isShared = True

        # Done
        self.setStatusText ("Sharing initiated.")

    def displaySMTPSendSuccess (self, mailMessageUUID):
        """
          Called when the SMTP Send was successful.
        """
        mailMessageKind = Mail.MailParcel.getMailMessageKind ()
        mailMessage = mailMessageKind.findUUID(mailMessageUUID)
    
        if mailMessage is not None and mailMessage.isOutbound:
            self.setStatusText ('mailMessage "%s" sent.' % mailMessage.about)

    def displaySMTPSendError (self, mailMessageUUID):
        """
          Called when the SMTP Send generated an error.
        """
        # Lookup the message
        mailMessageKind = Mail.MailParcel.getMailMessageKind ()
        mailMessage = mailMessageKind.findUUID(mailMessageUUID)
    
        if mailMessage is not None and mailMessage.isOutbound:
            """DLDTBD - Select the message in CPIA"""
    
            errorStrings = []
    
            for error in mailMessage.deliveryExtension.deliveryErrors:
                 errorStrings.append(error.errorString)
   
            str = "error"
   
            if len(errorStrings) > 1:
                str = "errors"
   
            errorMessage = "The following %s occurred. %s" % (str, ', '.join(errorStrings))
            errorMessage = errorMessage.encode ('utf-8')
            self.setStatusText (errorMessage)
            application.dialogs.Util.showAlert(Globals.wxApplication.mainFrame, errorMessage)
            self.setStatusText ('')
        