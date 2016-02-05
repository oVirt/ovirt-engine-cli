
import os

if os.name == "posix":
    from ovirtcli.platform.posix import util
    from ovirtcli.platform.posix import vnc
    from ovirtcli.platform.posix import spice
    from ovirtcli.platform.posix import ssh

else:
    pass
