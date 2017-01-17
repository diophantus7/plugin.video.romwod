# -*- encoding: utf-8 -*-
# Module: main
# Author: diophantus7
# Created on: December 2nd, 2016
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from resources.lib.pluginhandler import PluginHandler

__PluginHandler__ = PluginHandler()

if __name__ == '__main__':
    #router(sys.argv[2][1:])
    __PluginHandler__.run()
