
import os
from cli.error import Error
from ovirtcli.platform import util


def launch_vnc_viewer(host, port, ticket, debug=False):
    """Launch a VNC viewer on host::port with `password'."""
    display = os.environ.get('DISPLAY')
    if display is None:
        raise Error, 'not running in a GUI, cannot start a VNC viewer'
    cmd = util.which('vncviewer')
    if cmd is None:
        raise Error, 'vncviewer: command not found'
    args = ['vncviewer', '%s::%s' % (host, port), '-passwdInput' ]
    pid, pstdin = util.spawn(cmd, args, debug)
    os.write(pstdin, ticket)
    os.close(pstdin)
