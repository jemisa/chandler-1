__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2003 Open Source Applications Foundation"
__license__ = "OSAF License"


import os
import webbrowser
from wxPython.wx import *
from wxPython.html import *

class SplashScreen(wxFrame):
    """
      This class implements an HTML informational screen presented to the user. 
    Common uses are for splash screens or 'About' pages.
    The page can be dismissed either by clicking on it or by a timer.
    """
    def __init__(self, title="", pageLocation="", useTimer=true, timerLength=10000):
        """
          Sets up the splash screen and starts its timer.
        """
        wxFrame.__init__(self, None, -1, title, 
                         size = (700,450),
                         style=wxSTAY_ON_TOP|\
                         wxDEFAULT_FRAME_STYLE)
        panel = HTMLPanel(self, pageLocation)
        self.CentreOnScreen()
        
        if useTimer:
            self.timer = SplashTimer(self)
            self.timer.Start(timerLength)
        else:
            self.timer = None
            
        EVT_CLOSE(self, self.OnCloseWindow)
        
    def OnCloseWindow(self, event):
        """
          Stops the timer from running and closes the window.
        """
        if self.timer != None:
            self.timer.Stop()
        self.Destroy()
        
class HTMLPanel(wxHtmlWindow):
    """
      Displays the html message.
    """
    def __init__(self, parent, pageLocation):
        """
          Sets up the wxHtmlWindow and loads the proper page to be displayed.
        """
        wxHtmlWindow.__init__(self, parent, style = wxHW_SCROLLBAR_NEVER)
        self.parent = parent
        self.LoadPage(pageLocation)
        
    def OnCellClicked(self, cell, x, y, event):
        """
          Called whenever the splash screen is clicked.  If a link was
        clicked, then that link will be opened.  Otherwise, we close the
        splash screen.
        """
        self.linked = false
        wxHtmlWindow.base_OnCellClicked(self, cell, x, y, event)
        if not self.linked:
            self.parent.Close()
        
    def OnLinkClicked(self, link):
        """
          Called whenever a link on the splash screen is clicked.  Opens that
        url in the user's default web browser.
        """
        self.linked = true
        webbrowser.open(link.GetHref())
    
class SplashTimer(wxTimer):
    """
      A timer that keeps track of how long the splash screen has been 
    displayed.
    """
    def __init__(self, window):
        """
          Sets up the timer.
        """
        wxTimer.__init__(self)
        self.window = window
        
    def Notify(self):
        """
          When the timer has expired, we notify the splash screen that it is
        time to close.
        """
        self.window.Close()
        
        
