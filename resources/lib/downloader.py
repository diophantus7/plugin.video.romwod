import sys
import os
import xbmc
import xbmcaddon
import re
import requests
import pickle
from BeautifulSoup import BeautifulSoup
from utils import notify

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
    
TEMP_PATH  = xbmc.translatePath("special://temp")
COOKIE_PATH = os.path.join(TEMP_PATH, 'romwod.cookies')

class LoginError(Exception):
    def __init__(self, message):
        self.message = message


class DownloadHandler:
    
    
    def __init__(self):
        self.session = requests.session()

        if os.path.isfile(COOKIE_PATH):
            self.session.cookies = self._get_cookies()
        
        if (bool(self.session.cookies) is False or
            next(cookie for cookie in self.session.cookies
                 if cookie.name == 'amember_nr').is_expired()):
            try:
                self._sign_in()
                xbmc.log("Signing in...")
            except LoginError as err:
                notify('Login Error', err.message)
                sys.exit()
            self._save_cookies()
    
    
    def get(self, url):
        site = self.session.get(url)
        redirects = self._redirects(site)
        if redirects:
            site = self.session.get(redirects)
        return site
            

    def _sign_in(self):
        _login_url = 'https://romwod.com/members/login/'
        username = __addon__.getSetting('username')
        password = __addon__.getSetting('password')
        if username and password:
            #session = requests.session()
            login_data = dict(amember_login = username, amember_pass = password)
            dashboard = self.session.post(_login_url, data=login_data)
            if self._incorrect_login_credentials(dashboard.content):
                raise LoginError("Please check username and password")
            elif self._signed_in(dashboard.content, username):
                return dashboard
            else:
                raise Exception()
        else:
            raise LoginError("Please specify username and password in settings")


    def _signed_in(self, content, username):
        if re.search(username, content, re.IGNORECASE):
            return True
        else:
            return False
        

    def _incorrect_login_credentials(self, content):
        if re.search("user name or password is incorrect", content, re.IGNORECASE):
            return True
        else:
            return False


    def _redirects(self, site):
        soup = BeautifulSoup(site.content)
        location = re.search('window\.location\s*=\s*\"([^"]+)\"', str(soup))
        if location:
            return location.group(1)
        else:
            return False


    def _save_cookies(self):
        with open(COOKIE_PATH, 'w') as f:
            pickle.dump(self.session.cookies, f)
        
        
    def _get_cookies(self):
        with open(COOKIE_PATH) as f:
            return pickle.load(f)
        