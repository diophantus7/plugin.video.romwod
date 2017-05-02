import requests
import re
import urlparse
from collections import OrderedDict

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup
        
from downloader import (DownloadHandler,
                        LoginError)

from utils import get_daytime
from constants import *


class RomwodPage:
    
    def __init__(self, url, needsLogin):
        self._url = url
        if needsLogin:
            session = DownloadHandler()
        else:
            session = requests.session()
        self._content = session.get(url).content
        redirect = self._redirects()
        if redirect:
            self._content = session.get(redirect).content
        self._parser = BeautifulSoup(self._content)
        if self._is_login_page():
            raise LoginError("Page %s needs login." % self._url)
    
    def _redirects(self):
        soup = BeautifulSoup(self._content)
        location = re.search('window\.location\s*=\s*\"([^"]+)\"', str(soup))
        if location:
            return location.group(1)
        else:
            return False
        
    def _is_login_page(self):
        if self._parser.findAll('div', {'id':'forgotPass'}):
            return True
        else:
            return False
  
    def get_content(self):
        return self._content

    def extract_video_blocks(self):
        """
        Extracts the video block from the html code as used on
        the romwod site
        
        :param html: str
        """
        parsed_html = BeautifulSoup(self._content)
        video_blocks_dict = json.loads(bs.find('div', {'data-react-class':'WeeklySchedule'})['data-react-props'])
        return video_blocks_dict['schedule']['scheduled_workouts']
        #return parsed_html.body.findAll(
            #'div', attrs={'class':re.compile(r"video-block\s.*")})
    
    def extract_selection_form(self):
        """
        Extracts the selection form which is used to filter the workouts
        by classes
        
        :param site: str
        """
        bs = BeautifulSoup(self._content)
        form = bs.body.find('form',
                            attrs={'class':'searchandfilter class_filter_search'})
        return str(form)    
    
    def extract_options(self):
        """
        Extracts the options for which one can filter the workouts
        
        :param site: str
        """
        form = BeautifulSoup(self.extract_selection_form(),
                             convertEntities=BeautifulSoup.HTML_ENTITIES)
        node = form.div.ul.li
        opt_dict = OrderedDict()
        while node.h4 is not None:
            opt_dict[node.h4.text] = [(x.text, x.input['name'][2:-2])
                                      for x in node.findAll('li')]
            node = node.nextSibling
        return opt_dict


    def next_page(self):
        """
        Checks if the content listed on the webpage goes on for
        several pages.
        If this is the case, the next page is returned,
        otherwise None.
        
        :param site: str
        """
        bs = BeautifulSoup(self._content)
        next = bs.find('a', attrs={'class':'nextpostslink'})
        if next:
            return next['href']
        else:
            return None
    

class Dashboard(RomwodPage):
    
    def __init__(self, url = DASHBOARD_URL, needsLogin = False):
        RomwodPage.__init__(self, url, needsLogin)
        
    def get_dashboard_entries(self):
        return self._parser.find(
            'div', {'class':'container','id':'dash-options'}).findAll(
            'div', {'class':re.compile('dash-option\s')})
#     
#         listing = []
#         
#         if db_options is not None:
#             for option in db_options:
#                 listing.append(self.get_dashboard_item(option))
#         
#         return listing
    
    def get_dashboard_item(self, option_block):
        parsed = urlparse.urlparse(self._url)
        lparsed = list(parsed)
        lparsed[2] = option_block.a.get('href')
        lparsed[4] = 'action=list'
        item = xbmcgui.ListItem(label=option_block.h3.text)
        return FolderItem(option_block.h3.text,
                          urlparse.urlunparse(lparsed),
                          option_block.img.get('src')).get_list_item()

    
    def get_dashboard_fanart(self):
        fanart = FANART_BASE + 'dash-bg-' + get_daytime() + '.jpg'
        return fanart
    
    