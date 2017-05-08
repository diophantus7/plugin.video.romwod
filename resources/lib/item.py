import sys
import xbmcgui
import os
import urllib
import xbmc

from constants import *



class VideoItem(tuple):
    
    def __new__(cls, video):
        item = xbmcgui.ListItem(label=video.title)
        item.setInfo('video', {'title': video.title,
                                    'duration': video.duration,
                                    'Plot': video.description + video.get_tags()})
        item.setArt({'thumb': video.thumbnail})
        item.setProperty('IsPlayable', 'true')
        #list_item.setProperty('mimetype', 'video/x-msvideo')
        from pluginhandler import PluginHandler
        ph = PluginHandler()
        #url = ph.http_to_plugin_url(video.link)
        url = ph.http_to_plugin_url(WORKOUTS_URL + video.wistia_id)
        xbmc.log(url)
        context_menu_items = [(ADD_FAVORITES,
                               'XBMC.RunPlugin(%s)' % ph.append_path('clear'))]
        context_menu_items.append(
            (REMOVE_FAVORITES,
             'XBMC.RunPlugin(%s?q=%s)' % (ph.append_path('remove'), 'remove')))
        return tuple.__new__(cls, (url, item, False))


class FolderItem(tuple):
    
    def __new__(cls, label, url, thumb = None):
        item = xbmcgui.ListItem(label=label)
        #FolderItem.__init__(label, url, thumb)
        return tuple.__new__(cls, (url, item, True))
    
    def __init__(self, label, url, thumb = None):
        pass
    
#     def __init__(self, label, url, thumb = None):
#         self._item = xbmcgui.ListItem(label=label)
#         if thumb is not None:
#             self._item.setArt({'thumb':thumb})
#         self._url = url

    
class HistoryItem(FolderItem):

    
    def __init__(self, label, url, thumb = None):
        from pluginhandler import PluginHandler
        ph = PluginHandler()
        context_menu_items = [(CLEAR_HISTORY,
                                         'XBMC.RunPlugin(%s)'
                                         % ph.append_path('clear'))]
        context_menu_items.append(
            (REMOVE_ENTRY,
             'XBMC.RunPlugin(%s?q=%s)' % (ph.append_path('remove'), label)))
        self[1].addContextMenuItems(context_menu_items)
         