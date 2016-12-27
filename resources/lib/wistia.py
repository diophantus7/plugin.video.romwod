import re
import requests

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup


_JSON_URL = "http://fast.wistia.com/embed/medias/%s.json"
_IFRAME_URL = "http://fast.wistia.net/embed/iframe/%s"


class WistiaExtractor:
    
    def __init__(self, html_page, format):
        self.html_page = html_page
        self.video_id = self._extract_video_id()
        self._format = format
    
        
    def _extract_video_id(self):
        bs = BeautifulSoup(self.html_page)
        return re.search('wistia_async_([0-9a-z]*) ', str(bs)).group(1)
    
    
    def _download_json(self):
        s = requests.Session()
        s.headers.update({'referer':_IFRAME_URL % self.video_id})
        req = s.get(_JSON_URL % self.video_id)
        return req.json()
    
    
    def get_video_url(self):
        json_data = self._download_json()
        #return json_data['media']['unnamed_assets'][12]['url']
        xbmc.log(json_data['media']['unnamed_assets'][12]['url'])
        return next(d['url'] for d in json_data['media']['unnamed_assets']
                    if d['display_name'] == self._format and d['ext'] == 'm3u8')
