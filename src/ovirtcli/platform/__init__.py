
import sys

if sys.platform in ('linux2',):
    from ovirtcli.platform.posix import util
    from ovirtcli.platform.posix import vnc
    from ovirtcli.platform.posix import spice
    from ovirtcli.platform.posix import ssh

elif sys.platform in ('win32',):
    pass
