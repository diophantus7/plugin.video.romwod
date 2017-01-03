import sys
import xbmcgui
import os
import urllib


_url = sys.argv[0]


class FolderItem:
    
    
    def __init__(self, label, params, thumb = None):
        self._item = xbmcgui.ListItem(label=label)
        if thumb is not None:
            self._item.setArt({'thumb':thumb})
        self._url = _url + '?' + urllib.urlencode(params)
        
    def get_item(self):
        return (self._url, self._item, True)