import xbmc
import re
from collections import OrderedDict

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup


# def get_video_id(wod_page):
#     bs = BeautifulSoup(wod_page)
#     return re.search('wistia_async_([0-9a-z]*) ', str(bs)).group(1)


def notify(title, message):
    xbmc.executebuiltin("XBMC.Notification(%s, %s)" % (title, message))


def extract_video_blocks(html):
    parsed_html = BeautifulSoup(html)
    return parsed_html.body.findAll('div',
                                attrs={'class':re.compile(r"video-block\s.*")})

def extract_selection_form(site):
    bs = BeautifulSoup(site)
    form = bs.body.find('form',
                        attrs={'class':'searchandfilter class_filter_search'})
    return str(form)
    
def extract_options(site):
    form = BeautifulSoup(extract_selection_form(site))
    node = form.div.ul.li
    opt_dict = OrderedDict()
    while node.h4 is not None:
        opt_dict[node.h4.text] = [(x.text, x.input['name'][2:-2]) for x in node.findAll('li')]
        node = node.nextSibling
    return opt_dict