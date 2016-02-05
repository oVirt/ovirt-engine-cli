
import os

if os.name == "posix":
    from cli.platform.posix.terminal import PosixTerminal as Terminal
    from cli.platform.posix.util import *

else:
    pass
