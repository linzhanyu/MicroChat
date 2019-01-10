# -*- coding:utf-8 -*-

import sys, os

dirname = __path__[0]
if sys.platform == 'win32':
    __path__.insert( 0, os.path.join( dirname, 'Windows' ) )
elif sys.platform == 'darwin':
    __path__.insert( 0, os.path.join( dirname, 'Mac' ) )
elif sys.platform == 'linux':
    __path__.insert( 0, os.path.join( dirname, 'Linux' ) )

from .Console import Console
if sys.platform == 'win32':
    from .SubProcess import SubProcess

console = Console()

__all__ = ['Console', 'console' ]
if sys.platform == 'win32':
    __all__.append( 'SubProcess' )

