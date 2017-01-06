import sys
import xbmcgui
import os
import urllib
import xbmc


_url = sys.argv[0]

CLEAR_HISTORY = "Clear History"
REMOVE_ENTRY = "Remove entry"

class FolderItem:
    
    
    def __init__(self, label, params, thumb = None):
        self._item = xbmcgui.ListItem(label=label)
        if thumb is not None:
            self._item.setArt({'thumb':thumb})
        self._url = _url + 'wod/?' + urllib.urlencode(params)
        
        
    def get_item(self):
        return (self._url, self._item, True)
    
    
class HistoryItem(FolderItem):
    
    def __init__(self, label, params, thumb = None):
        FolderItem.__init__(self, label, params, thumb)
        context_menu_items = [(CLEAR_HISTORY,
                                         'XBMC.RunPlugin(%s?action=clear)'
                                         % _url)]
        context_menu_items.append(
            (REMOVE_ENTRY,
             'XBMC.RunPlugin(%s?action=remove&selection=%s)' % (_url, label)))
        self._item.addContextMenuItems(context_menu_items)
    