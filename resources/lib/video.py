import sys
import urllib
import re
import xbmcgui

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup

_url = sys.argv[0]
_handle = int(sys.argv[1])

POSTER_CROP = "?crop=middle&fit=crop&h=1345&ixjsv=2.1.0&w=900"
    
class Video:

    def __init__(self, video_block):
        bs = BeautifulSoup(str(video_block),
                           convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.title = bs.find('span',attrs={'class':'video-name'}).text
        self.duration = bs.find('div',attrs={'class':'video-duration'}).text
        self.description = bs.find('p',attrs={'class':'video-description'}).text
        vid_tags = bs.findAll('li')
        self.tags = [tag.text for tag in vid_tags]
        self.link = video_block.a.get('href')
        self.thumbnail = video_block.img.get('data-src')
        self._set_url_title()

    
    def get_list_item(self):
        """
        Returns the xbmcgui.Listitem for the video
        
        """
        list_item = xbmcgui.ListItem(label=self.title)
        list_item.setInfo('video', {'title': self.title,
                                    'duration': self.duration,
                                    'Plot': self.description + self._get_tags()})
        list_item.setArt({'icon': self.thumbnail})
        list_item.setProperty('IsPlayable', 'true')
        list_item.setProperty('mimetype', 'video/x-msvideo') 
        url = '{0}?action=play&video={1}'.format(_url,
                                                 urllib.quote(self.url_title))
        is_folder = False    
        return (url, list_item, is_folder)    
    
    
    def _get_tags(self):
        return "[CR]" + ' | '.join(["[LIGHT][I]" + tag
                                    + "[/I][/LIGHT]" for tag in self.tags])
    
    
    def _set_url_title(self):
        """
        Sets the title of the video as in the url.
        This is needed to resolve the video.
        
        """
        self.url_title = self.link.split('/')[-2]
    
    
    def _get_video_id(self, downloader):
        video_page = downloader.get(self.link).content
        bs = BeautifulSoup(video_page)
        return re.search('wistia_async_([0-9a-z]*) ', str(bs)).group(1)

