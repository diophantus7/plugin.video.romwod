import sqlite3
import datetime
import os
import xbmc
import xbmcaddon

__addon__ = xbmcaddon.Addon()

DATA_PATH = xbmc.translatePath('special://profile/addon_data/%s'
                               % __addon__.getAddonInfo('id')).decode('utf-8')
HISTORY_PATH = os.path.join(DATA_PATH, 'searchhistory.sqlite')

TABLE_NAME = "search_history"

class SearchHistory:
    
    
    def __init__(self):
        self._conn = sqlite3.connect(HISTORY_PATH)
        self._conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        self._cursor = self._conn.cursor()
        create_tab_cmd = ('CREATE TABLE IF NOT EXISTS %s'
                          '(key TEXT PRIMARY KEY, time TIMESTAMP)'
                          % TABLE_NAME
                          )
        self._cursor.execute(create_tab_cmd)
            
    
    def __enter__(self):
        self.__init__()
        return self
    
    
    def update(self, search_string):
        now = datetime.datetime.now()
        update_cmd = 'REPLACE INTO %s (key, time) VALUES (?,?);' % TABLE_NAME
        self._cursor.execute(update_cmd, (search_string, now))
        
        
    def clear(self):
        delete_all_cmd = 'DELETE FROM %s;' % TABLE_NAME
        self._cursor.execute(delete_all_cmd)
    
    
    def delete(self, string):
        del_cmd = 'DELETE FROM %s WHERE key = ?;' % TABLE_NAME
        self._cursor.execute(del_cmd, [string])

    
    def get_entries(self):
        select_cmd = 'SELECT key FROM %s ORDER BY time DESC;' % TABLE_NAME
        self._cursor.row_factory = lambda cursor, row: row[0]
        return self._cursor.execute(select_cmd).fetchall()

    
    def __exit__(self, type, value, traceback):
        self._close()
        
    def _close(self):
        self._conn.commit()
        self._conn.close()
            

        