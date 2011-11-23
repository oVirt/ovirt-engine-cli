
import sys

if sys.platform in ('linux2',):
    from src.ovirtcli.platform.posix import util
    from src.ovirtcli.platform.posix import vnc
    from src.ovirtcli.platform.posix import spice

elif sys.platform in ('win32',):
    pass
