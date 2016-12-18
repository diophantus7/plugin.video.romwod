import re

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup


def get_video_id(wod_page):
    bs = BeautifulSoup(wod_page)
    return re.search('wistia_async_([0-9a-z]*) ', str(bs)).group(1)


def extract_video_blocks(html):
    parsed_html = BeautifulSoup(html)
    return parsed_html.body.findAll('div',
                                attrs={'class':re.compile(r"video-block\s.*")})

