# -*- coding:utf-8 -*-
from __future__ import print_function
import sys
if sys.version_info.major == 2:
    import Core
elif sys.version_info.major == 3:
    from Core import Core

import unittest

def RunUI() :
    from ClientApp import App
    app = App( redirect = False )
    app.MainLoop()

def RunConsole() :
    # print('Console mode ... unfinished.')
    # pass
    Core.core.MainLoop()

def Run( console = False ) :
    # print( dir(Core.Core) )
    if not Core.core.Init() :
        return False
    if console :
        RunConsole()
    else:
        RunUI()
    Core.core.Fini()

# ------------------------------------------------------------
# UnitTest
# ------------------------------------------------------------
def suite():
    suite = unittest.TestSuite()
    suite.addTest( Core.suite() )
    return suite

