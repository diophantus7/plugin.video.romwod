import sys
import os
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import urllib
import urlparse
import datetime
import requests
import re
import json

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup

from constants import *
from downloader import DownloadHandler
from utils import extract_options
from video import Video
from video import VideoBlocksHandler
from item import *
from resources.lib.search_history import SearchHistory
from page import (RomwodPage,
                  Dashboard)
from wistia import WistiaExtractor


class PluginHandler(object):
    

    def __init__(self):
        self._addon = xbmcaddon.Addon()
        self._addonname = self._addon.getAddonInfo('name')
        self._url = sys.argv[0] + sys.argv[2]
        self._handle = int(sys.argv[1])
        parsed = urlparse.urlparse(self._url)
        self._parsed = parsed
        self._path = parsed.path
        self._query = parsed.query
        self._params = self.get_params()
        self.addon_path = xbmc.translatePath(
            self._addon.getAddonInfo('path')).decode('utf-8')
        self.img_path = os.path.join(self.addon_path, 'resources', 'media')
    
        
    def get_params(self):
        return dict(urlparse.parse_qsl(self._query))
    
    def get_cookie_path(self):
        data_path = xbmc.translatePath(
            'special://profile/addon_data/%s'
            % self._addon.getAddonInfo('id')).decode('utf-8')
        return os.path.join(data_path, COOKIE_FILE_NAME)
    
    
    def notify(title, message):
        xbmc.executebuiltin("XBMC.Notification(%s, %s)" % (title, message))

    
    def get_username(self):
        return self._addon.getSetting('username')
    
    def get_password(self):
        return self._addon.getSetting('password')

    def get_http_url(self):
        lreplaced = list(self._parsed)
        lreplaced[0] = 'https'
        lreplaced[1] = HOST
        return urlparse.urlunparse(lreplaced)
    
    def http_to_plugin_url(self, url):
        lreplaced = list(urlparse.urlparse(url))
        lreplaced[0] = 'plugin'
        lreplaced[1] = self._parsed.netloc
        return urlparse.urlunparse(lreplaced)
    
    def add_action_to_url(self, url, action):
        return '%s?action=%s' % (url, action)
    
    def add_query_to_url(self, query):
        return self._url + urllib.urlencode(query)
        
    def get_new_url(self, path = '/', query = ''):
        lreplaced = list(self._parsed)
        lreplaced[2] = '/' + path.strip('/') + '/' if path is not '/' else path
        lreplaced[4] = query
        return urlparse.urlunparse(lreplaced)
    
    def append_path(self, path_ext):
        return self.get_new_url(self._path + path_ext)
    
    
    def get_video_format(self):
        return self._addon.getSetting('video_format')


    def resolve(self):
        """
        Resolves the video to its url. Just needs the
        title of the video as in the url. See play_video
        :param title: str
        """
        #video_page = RomwodPage(self.get_http_url(), needsLogin=False)
        #xbmc.log(self.get_http_url())
        video_id = self._path.split('/')[-1]
        #video_id = "buo8a1mu83"
        # Look into external_id and short_external_id
        # curl "http://fast.wistia.net/oembed?url=https%3A%2F%2Fsupport.wistia.com%2Fmedias%2Fnb4ymq0ugz&embedType=iframe"
        # where nb4ymq0ugz is the external_id
        
        #xbmc.log(self._path)
        we = WistiaExtractor(video_id, self.get_video_format())
        try:
            return we.get_video_url()
        except ResolveError as err:
            xbmc.log(err.message)
            sys.exit()
    
    
    def play_video(self):
        """
        Plays a video after resolving the URL. It takes the title
        of the video as it is called in the url of the video.
        E.g. for the video on romwod.com/workout/video-title it
        is video-title
    
        :param title: str
        """
        url = self.resolve()
        xbmc.log("heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeey")
        xbmc.log(url)
        play_item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self._handle, True, listitem=play_item)
    
    
    
    def list_wods(self):
        """
        Lists all the videos found on the website with path of the plugin.
        
        """
        url = self.get_http_url()

        page = RomwodPage(url, False)
        vh = VideoBlocksHandler(page.extract_video_blocks())
        videos = vh.get_videos()
        
        listing = []
        for video in videos:
            listing.append(VideoItem(video))
#             item = xbmcgui.ListItem(label=video.title)
#             item.setProperty(u'IsPlayable', u'true')
#             xbmcplugin.addDirectoryItem(handle=self._handle,
#                                         url=str(self.http_to_plugin_url(video.link)),
#                                         #url=u'plugin://plugin.video.romwod/workout/timber/',
#                                         listitem=item,
#                                         isFolder=False)
        
        next = page.next_page()
        if next is not None:
            listing.append(FolderItem(
                NEXT_PAGE_LABEL,
                self.add_action_to_url(self._url + next, 'list'
                )))
    
        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))
        xbmcplugin.endOfDirectory(self._handle)


    def search(self):
        listing = []
        NEW_SEARCH = "[B][I]New Search...[/I][/B]"
        listing.append(FolderItem(NEW_SEARCH, self.append_path('input')))
        with SearchHistory() as history:
            for entry in history.get_entries():
                query = {'q':entry.encode('ascii', 'xmlcharrefreplace')}
                listing.append(HistoryItem(entry, self.get_new_url(path = 'search', query = urllib.urlencode(query))))
            
        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))
        xbmcplugin.endOfDirectory(self._handle)
    
    
    def new_search(self):
        """
        This function handles asks the user for the
        search string and then lists all videos found
        on romwod.com
        
        """
        dialog = xbmcgui.Dialog()
        search_string = dialog.input('Search for workouts containing:',
                                     type=xbmcgui.INPUT_ALPHANUM)
        if search_string is not '':
            with SearchHistory() as history:
                history.update(search_string)
        #query = {'s':search_string, 'post_type':'workouts'}
        query = {'q':search_string}
        xbmc.executebuiltin('Container.Update(%s)'
                            % self.get_new_url(path = 'search', query = urllib.urlencode(query)))
    
    
    def select(self):
        """
        This filters videos. It asks the user for the purpose
        and/or a body part and then lists the videos it finds
        with the user's selection
        
        """
        page = RomwodPage(WORKOUTS_URL, needsLogin = False)
        
        dialog = xbmcgui.Dialog()
        options = page.extract_options()
    
        #top_opts = [key for key in options]
        selection = {}
        for key in options:
            opt = [value for value in options[key]]
            selection[key] = dialog.select(key, opt)
    
        query = {}
        query_string = ''
        for key in options:
            if selection[key] is not -1:
                opt = [value for value in options[key]][selection[key]]
                query[opt[1]] = opt[0].replace('+','').replace(' ', '-')
                query_string = ' + '.join(filter(None, [query_string, opt[0]]))
        
    #     #TODO save query in nice way but still manageable for history... 
    #     if query_string is not None:
    #         with SearchHistory() as history:
    #             history.update(query_string)
    
        xbmc.executebuiltin('Container.Update(%s)'
                            % self.get_new_url(path = 'search', query = urllib.urlencode(query)))
    
    
    def list_wod_schedule(self):
        page = RomwodPage(SCHEDULE_URL, needsLogin=False)
        bs = BeautifulSoup(page.get_content(),
                           convertEntities=BeautifulSoup.HTML_ENTITIES)
        listing = []
        schedule_archive = json.loads(bs.find('div',  {'data-react-class':'ScheduleArchive'})['data-react-props'])['schedules']
        for week in schedule_archive:
            listing.append(
                FolderItem(week['title'], self.get_new_url("wod/" + week['slug']),
                                      FANART_BASE + "members-titlebar-bg17.jpg"
                                      + CROP_256
                                      ))
        
        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))
        xbmcplugin.endOfDirectory(self._handle)

    
    def get_dashboard_item(self, option_block):
        parsed = self._parsed
        lparsed = list(parsed)
        lparsed[2] = option_block.a.get('href')
        #lparsed[4] = 'action=list'
        #item = xbmcgui.ListItem(label=option_block.h4.text)
        return FolderItem(option_block.h4.text,
                          urlparse.urlunparse(lparsed),
                          option_block.img.get('src'))


    def list_dashboard(self, todays_video):
        """
        List the content of the dashboard as on romwod.com/wod/.
        Takes today's routine and lists it as first entry.
        
        :param todays_video: Video
        """
        todays_video_item = VideoItem(todays_video)
        todays_video_item[1].setLabel(label="Today's WOD | [I]%s[/I]"
                                      % todays_video.title)
        listing = [todays_video_item]  
        
        db = Dashboard()
        #listing.extend(db.get_dashboard_items())
        for entry in db.get_dashboard_entries():
            listing.append(self.get_dashboard_item(entry))
             
        listing.append(FolderItem(PAST_WODS, self.get_new_url('all-wods')))
        listing.append(FolderItem(SEARCH,
                                  self.get_new_url(path='search'),
                                  os.path.join(self.img_path,
                                               "searchicon.png")))
#         listing.append(FolderItem(FILTER,
#                                   self.get_new_url('filter'),
#                                   os.path.join(self.img_path,
#                                                "filtericon.png")))
          
        for item in listing:
            item[1].setArt({'fanart':db.get_dashboard_fanart() + HD_CROP})
        
        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))
        xbmcplugin.endOfDirectory(self._handle)


    def initialize(self):
        """
        This function is called upon the first call of the plugin.
        It signs in to the site via the DownloadHandler, and then
        lists the content of the dashboard.
        
        """
        now = datetime.datetime.now()
        WOD_URL = "https://app.romwod.com/wod?user_date=" + now.strftime("%Y-%m-%d")
        wod_page = RomwodPage(WOD_URL, needsLogin=False)
#         dh = DownloadHandler()
#         week_view = dh.get(WOD_URL)
        
        video_blocks = wod_page.extract_video_blocks()
        video = Video(video_blocks[datetime.date.today().weekday()])

        self.list_dashboard(video)
    
    def run(self):
        """
        This function routes the paramstring to the
        right function
    
        """
        xbmc.log("halloooooooooooooooooooooooooooo")
        xbmc.log(self._path)
        
        if self._path is not '/' or self._query is not '':
            path = self._path.strip('/').split('/')
            xbmc.log("halloooooooooooooooooooooooooooo")
            if path[0] == 'workout' and len(path) > 1:
                xbmc.log("halloooooooooooooooooooooooooooo")
                self.play_video()
            elif path[0] == 'all-wods':
                self.list_wod_schedule()
            elif path[0] == 'search':
                if len(path) == 1:
                    if self._query == '':
                        self.search()
                    else:
                        self.list_wods()
                elif path[1] == 'input':
                    self.new_search()
                elif path[1] == 'clear':
                    with SearchHistory() as history:
                        history.clear()
                    xbmc.executebuiltin('Container.Refresh')
                elif path[1] == 'remove':
                    with SearchHistory() as history:
                        history.delete(self._params['q'])
                    xbmc.executebuiltin('Container.Refresh')
            elif path[0] == 'filter':
                self.select()
            else:
                self.list_wods()
        else:
            self.initialize()
