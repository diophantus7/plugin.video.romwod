import re
import requests
import xbmc

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup


_JSON_URL = "http://fast.wistia.com/embed/medias/%s.json"
_IFRAME_URL = "http://fast.wistia.net/embed/iframe/%s"


class ResolveError(Exception):
    def __init__(self, message):
        self.message = message
        

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
        try:
            url = next(d['url'] for d in json_data['media']['unnamed_assets']
                    if d['display_name'] == self._format and d['ext'] == 'm3u8')
        except:
            video_data = [d for d in json_data['media']['unnamed_assets']
                         if d['status'] == 2 and 'opt_vbitrate' in d
                         and 'display_name' in d and
                         'p' in d['display_name']]
            if not video_data:
                raise ResolveError("No video found.")
            url = max(video_data,
                      key=lambda d: int(d['display_name'].strip('p')))['url']
            xbmc.log("Fallback to url: %s" % url)
        return url
