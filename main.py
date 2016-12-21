# -*- encoding: utf-8 -*-
# Module: main
# Author: Stefan
# Created on: December 2nd, 2016
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
from urlparse import parse_qsl

import requests
import re
import datetime
import urllib
import os

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')

ADDON_PATH = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')
IMG_PATH = os.path.join(ADDON_PATH, 'resources', 'media')

sys.path.append(os.path.join(ADDON_PATH, 'resources', 'lib'))
from downloader import DownloadHandler
from wistia import WistiaExtractor
from parse import extract_video_blocks
from video import Video
from parse import extract_options

_url = sys.argv[0]
_handle = int(sys.argv[1])

BASE_URL = "https://romwod.com/"
WORKOUTS_URL = "https://romwod.com/workout/"
WOD_URL = "https://romwod.com/wod/"

#TODO check for network error


def initialize():
    username = __addon__.getSetting('username')
    password = __addon__.getSetting('password')
    
    dh = DownloadHandler()
    week_view = dh.get(WOD_URL)
    
    video_blocks = extract_video_blocks(week_view.content)
    video = Video(video_blocks[datetime.date.today().weekday()])

    list_dashboard(video)
  

def next_page(site):
    bs = BeautifulSoup(site)
    next = bs.find('a', attrs={'class':'nextpostslink'})
    if next:
        return next['href']
    else:
        return None


def list_wods(params):
    downloader = DownloadHandler()
  
    url = BASE_URL + params
    video_listing = downloader.get(url)
   
    video_blocks = extract_video_blocks(video_listing.content)
        
    videos = extract_videos_from_blocks(video_blocks)
    
    listing = []
    for video in videos:
        listing.append(video.get_list_item())
    
    next = next_page(video_listing.content)
    if next is not None:
        next_page_item = xbmcgui.ListItem(label="NEXT PAGE")
        url = '{0}?action=list&selection={1}'.format(_url,
                                                     next[len(BASE_URL):])
        listing.append((url, next_page_item, True))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def extract_videos_from_blocks(video_blocks):
    videos = []
    for vid_blk in video_blocks:
        video = Video(vid_blk)
        videos.append(video)
    return videos


def list_dashboard(todays_video):
    todays_video_item = todays_video.get_list_item()
    todays_video_item[1].setLabel(label="Today's WOD | [I]%s[/I]"
                                  % todays_video.title)
    listing = [todays_video_item]
    programming_item = xbmcgui.ListItem(label="Daily programming")
    programming_item.setArt({'thumb':"https://optimize.romwod.com/core/uploads/dash-dailyprogramming.jpg"})
    programming_url = '{0}?action=list&selection={1}'.format(_url, "wod")
    listing.append((programming_url, programming_item, True))
    
    all_item = xbmcgui.ListItem(label="All workouts")
    all_item.setArt({'thumb':"https://optimize.romwod.com/core/uploads/dash-romyourway.jpg"})
    all_url = '{0}?action=list&selection={1}'.format(_url, "workouts")
    listing.append((all_url, all_item, True))
    
    poses_item = xbmcgui.ListItem(label="LEARN THE POSES")
    poses_item.setArt({'thumb':"https://optimize.romwod.com/core/uploads/dash-learnposes.jpg"})
    poses_url = '{0}?action=list&selection={1}'.format(_url, "type/learn-poses/")
    listing.append((poses_url, poses_item, True))

    search_item = xbmcgui.ListItem(label="Search...")
    search_item.setArt({'thumb':os.path.join(IMG_PATH, "searchicon.png")})
    search_url = '{0}?action=search'.format(_url)
    listing.append((search_url, search_item, True))
    
    select_item = xbmcgui.ListItem(label="Filter by...")
    select_item.setArt({'thumb':os.path.join(IMG_PATH, "filtericon.png")})
    select_url = '{0}?action=filter'.format(_url)
    listing.append((select_url, select_item, True))
    
    for item in listing:
        item[1].setArt({'fanart':"https://optimize.romwod.com/core/uploads/072016v2-slide1.jpg?crop=left&fit=crop&h=1080&ixjsv=2.1.0&w=1920"})
    
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def resolve(title):
    downloader = DownloadHandler()
    
    link = WORKOUTS_URL + urllib.unquote(title)
    video_page = downloader.get(link).content

    we = WistiaExtractor(video_page)
    return we.get_video_url()


def play_video(name):
    """
    Plays a video after resolving the URL.

    :param path: str
    """
    path = resolve(name)
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def search_func():
    """
    This function handles asks the user for the
    search string and then lists all videos found
    on romwod.com
    
    """
    dialog = xbmcgui.Dialog()
    search_string = dialog.input('Search for workouts containing:',
                                 type=xbmcgui.INPUT_ALPHANUM)
    query = {'s':search_string, 'post_type':'workouts'}
    list_wods('?' + urllib.urlencode(query))


def select_func():
    session = requests.session()
    page = session.get(WORKOUTS_URL)
    dialog = xbmcgui.Dialog()
    options = extract_options(page.content)
    xbmc.log(str(type(options)))
    top_opts = [key for key in options]
    selection = {}
    for key in options:
        opt = [x[0] for x in options[key]]
        selection[key] = dialog.select(key, opt)

    query = {}
    for key in options:
        if selection[key] is not -1:
            opt = options[key][selection[key]]
            query[opt[1]] = opt[0].replace(' ', '-')
    #xbmc.log(urllib.urlencode(query))

    list_wods('?' + urllib.urlencode(query))


def router(paramstring):
    """
    This function routes the paramstring to the
    right function

    :param paramstring:
    """
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'list':
             list_wods(params['selection'])
        if params['action'] == 'play':
            play_video(params['video'])
        if params['action'] == 'search':
            search_func()
        if params['action'] == 'filter':
            select_func()
    else:
        initialize()


if __name__ == '__main__':
    router(sys.argv[2][1:])
