import sys
import urllib
import re
import xbmcgui

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup
        
    
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
        from pluginhandler import PluginHandler
        ph = PluginHandler()
        url = ph.http_to_plugin_url(self.link)
        is_folder = False
        return (url, list_item, is_folder)    
    
    
    def _get_tags(self):
        return "[CR]" + ' | '.join(["[LIGHT][I]" + tag
                                    + "[/I][/LIGHT]" for tag in self.tags])
    
    
    def _get_video_id(self, downloader):
        video_page = downloader.get(self.link).content
        bs = BeautifulSoup(video_page)
        return re.search('wistia_async_([0-9a-z]*) ', str(bs)).group(1)


class VideoBlocksHandler:
    
    
    def __init__(self, html_code):
        self._html_code = html_code
        
        
    def get_video_blocks(self):
        """
        Extracts the video block from the html code as used on
        the romwod site
        
        :param html: str
        """
        html_parser = BeautifulSoup(self._html_code)
        return html_parser.body.findAll(
            'div', attrs={'class':re.compile(r"video-block\s.*")})
#         video_blocks = []
#         for block in blocks:
#             video_blocks.append(block)
#         return video_blocks
    
    
    def get_videos(self):
        """
        Extracts each html video block and instanciates
        a Video for it. Returns all videos in a list.
        
        :param video_blocks: str
        """
        videos = []
        for vid_blk in self.get_video_blocks():
            video = Video(vid_blk)
            videos.append(video)
        return videos

        