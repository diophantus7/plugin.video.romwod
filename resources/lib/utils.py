import xbmc
import re
from collections import OrderedDict

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup


def notify(title, message):
    xbmc.executebuiltin("XBMC.Notification(%s, %s)" % (title, message))


def extract_video_blocks(html):
    """
    Extracts the video block from the html code as used on
    the romwod site
    
    :param html: str
    """
    parsed_html = BeautifulSoup(html)
    return parsed_html.body.findAll('div',
                                attrs={'class':re.compile(r"video-block\s.*")})

def extract_selection_form(site):
    """
    Extracts the selection form which is used to filter the workouts
    by classes
    
    :param site: str
    """
    bs = BeautifulSoup(site)
    form = bs.body.find('form',
                        attrs={'class':'searchandfilter class_filter_search'})
    return str(form)
    
def extract_options(site):
    """
    Extracts the options for which one can filter the workouts
    
    :param site: str
    """
    form = BeautifulSoup(extract_selection_form(site))
    node = form.div.ul.li
    opt_dict = OrderedDict()
    while node.h4 is not None:
        opt_dict[node.h4.text] = [(x.text, x.input['name'][2:-2]) for x in node.findAll('li')]
        node = node.nextSibling
    return opt_dict


def next_page(site):
    """
    Checks if the content listed on the webpage goes on for
    several pages.
    If this is the case, the next page is returned,
    otherwise None.
    
    :param site: str
    """
    bs = BeautifulSoup(site)
    next = bs.find('a', attrs={'class':'nextpostslink'})
    if next:
        return next['href']
    else:
        return None
    