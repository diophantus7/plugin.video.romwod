import sys
import urllib
import re
import xbmcgui

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup
        
from constants import *
        
    
class Video:

    def __init__(self, video_block):
        bs = BeautifulSoup(str(video_block),
                           convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.title = video_block['video']['title']
        self.duration = video_block['video']['duration_in_seconds']
        self.description = video_block['video']['description']
        self.tags = [tag['content'] for tag in video_block['video']['poses']]
        self.link = WORKOUTS_URL + video_block['video']['slug']
        self.thumbnail = video_block['video']['thumbnail']['url']
        #self.wistia_id = video_block['video']['thumbnail']['external_id']

    
    def get_tags(self):
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

        