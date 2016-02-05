
import os

if os.name == "posix":
    from src.ovirtcli.platform.posix import util
    from src.ovirtcli.platform.posix import vnc
    from src.ovirtcli.platform.posix import spice

else:
    pass
