import os
import xbmc
import xbmcaddon
import re
import requests
import pickle
from BeautifulSoup import BeautifulSoup

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')

_tmp_path = "special://temp"


class LoginError(Exception):
    def __init__(self, message):
        self.message = message


class DownloadHandler:

    def __init__(self):
        self.session = requests.session()
        tmp_path = xbmc.translatePath(_tmp_path)
        cookie_path = os.path.join(tmp_path, 'romwod.cookies')
        if os.path.isfile(cookie_path):
            self.session.cookies = self._get_cookies(cookie_path)
        else:
            try:
                username = __addon__.getSetting('username')
                password = __addon__.getSetting('password')
                self._sign_in(username, password)
                self._write_cookies(cookie_path, self.session)
            except LoginError as err:
                notify('Login Error', err.message)
                sys.exit()
    
    
    def get(self, url):
        site = self.session.get(url)
        redirects = self._redirects(site)
        if redirects:
            site = self.session.get(redirects)
        return site
            

    def _sign_in(self, username, password):
        _login_url = 'https://romwod.com/members/login/'
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


    def _write_cookies(self, path, session):
        #TODO does path end with '/'?
        #TODO load path from settings
        with open(path, 'w') as f:
            pickle.dump(session.cookies, f)
        
        
    def _get_cookies(self, path):
        with open(path) as f:
            return pickle.load(f)
        