import sys
import os
import xbmc
import xbmcaddon
import re
import requests
import pickle

try: 
        from BeautifulSoup import BeautifulSoup
except ImportError:
        from bs4 import BeautifulSoup
        
from constants import *



class LoginError(Exception):
    def __init__(self, message):
        self.message = message


class DownloadHandler:
    
    
    def __init__(self):
        self.session = requests.session()
        
        from pluginhandler import PluginHandler
        ph = PluginHandler()
        self._cookie_path = ph.get_cookie_path()

        if os.path.isfile(self._cookie_path):
            self.session.cookies = self._get_cookies()
        
        if (bool(self.session.cookies) is False or
            next(cookie for cookie in self.session.cookies
                 if cookie.name == 'amember_nr').is_expired()):
            try:
                self._sign_in()
                xbmc.log("Signing in...")
            except LoginError as err:
                ph.notify('Login Error', err.message)
                xbmc.log("Login Error - " + err.message)
                sys.exit()
            self._save_cookies()
    
    
    def get(self, url):
        return self.session.get(url)
#         redirects = self._redirects(site)
#         if redirects:
#             site = self.session.get(redirects)
#         return site
            

    def _sign_in(self):
        from pluginhandler import PluginHandler
        ph = PluginHandler()
        username = ph.get_username()
        password = ph.get_password()
        if username and password:
            login_data = dict(email = username, password = password)
            dashboard = self.session.post(LOGIN_URL, data=login_data)
            if self._incorrect_login_credentials(dashboard.content):
                raise LoginError("Please check username and password")
            elif self._signed_in(dashboard.content, username):
                return
#             else:
#                 raise Exception()
        else:
            raise LoginError("Please specify username and password in settings")


    def _signed_in(self, content, username):
        if re.search(username, content, re.IGNORECASE):
            return True
        else:
            return False
        

    def _incorrect_login_credentials(self, content):
        if re.search("username or password is incorrect", content,
                     re.IGNORECASE):
            return True
        else:
            return False


    def _save_cookies(self):
        with open(self._cookie_path, 'w') as f:
            pickle.dump(self.session.cookies, f)
        
        
    def _get_cookies(self):
        with open(self._cookie_path) as f:
            return pickle.load(f)
        
        