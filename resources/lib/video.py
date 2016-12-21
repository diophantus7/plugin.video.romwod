import sys
import urllib
import urlparse
import json
import re
import requests
import xbmcgui
from BeautifulSoup import BeautifulSoup

_url = sys.argv[0]
_handle = int(sys.argv[1])

_JSON_URL = "http://fast.wistia.com/embed/medias/%s.json"
_IFRAME_URL = "http://fast.wistia.net/embed/iframe/%s"

    
class Video:

    #TODO this gets a video_block and then turns it into a string
    def __init__(self, video_block):
        bs = BeautifulSoup(str(video_block))
        self.title = bs.find('span',attrs={'class':'video-name'}).text
        self.duration = bs.find('div',attrs={'class':'video-duration'}).text
        self.description = bs.find('p',attrs={'class':'video-description'}).text
        vid_tags = bs.findAll('li')
        self.tags = [tag.text for tag in vid_tags]
        self.link = video_block.a.get('href')
        self.thumbnail = video_block.img.get('data-src')
        self._set_url_title()

    
    def get_list_item(self):
        list_item = xbmcgui.ListItem(label=self.title)
        list_item.setInfo('video', {'title': self.title,
                                    'duration': self.duration,
                                    'Plot': self.description})
        list_item.setArt({'icon': self.thumbnail})
        list_item.setProperty('IsPlayable', 'true')
        list_item.setProperty('mimetype', 'video/x-msvideo') 
        url = '{0}?action=play&video={1}'.format(_url,
                                                 urllib.quote(self.url_title))
        is_folder = False    
        return (url, list_item, is_folder)    
        
    
    def _set_url_title(self):
        self.url_title = self.link.split('/')[-2]
    
    
    def _get_video_id(self, downloader):
        video_page = downloader.get(self.link).content
        bs = BeautifulSoup(video_page)
        return re.search('wistia_async_([0-9a-z]*) ', str(bs)).group(1)


    def _get_video_url(self):
        json_data = self._download_json()
        # 12 is the number where the hashtag with the inspect element from ff
        # conincide
        return json_data['media']['unnamed_assets'][12]['url']
    
    
    # returns a dict of the json data
    def _download_json(self):
        s = requests.Session()
        s.headers.update({'referer':_IFRAME_URL % self.id})
        req = s.get(_JSON_URL % self.id)
        return req.json()
