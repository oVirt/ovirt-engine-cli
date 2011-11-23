
import sys

if sys.platform in ('linux2',):
    from cli.platform.posix.terminal import PosixTerminal as Terminal
    from cli.platform.posix.util import *

elif sys.platform in ('win32',):
    pass
