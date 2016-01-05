#
# Copyright (c) 2014 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os
import tempfile

from cli.error import Error
from cli.messages import Messages
from ovirtcli.platform import util
from subprocess import Popen, PIPE


# Template to generate the remote viewer configuration file:
CONFIG_TEMPLATE = u"""\
[virt-viewer]
type=vnc
host={host}
port={port}
password={ticket}
delete-this-file=1
title={title}:%d - Press SHIFT+F12 to Release Cursor
toggle-fullscreen=shift+f11
release-cursor=shift+f12
secure-attention=ctrl+alt+end
"""


def launch_vnc_client(host, port, ticket, title, debug=False):
    """Launch the VNC client."""

    # Check that there is a X display available:
    display = os.environ.get('DISPLAY')
    if display is None:
        raise Error, Messages.Error.CANNOT_START_CONSOLE_CLIENT % 'VNC'

    # Try to use remote viewer:
    cmd = util.which("remote-viewer")
    if cmd is not None:
        launch_remote_viewer(cmd, host, port, ticket, title, debug)
        return

    # Try to use vncviewer:
    cmd = util.which("vncviewer")
    if cmd is not None:
        launch_vncviewer(cmd, host, port, ticket, debug)
        return

    # No luck, no known command is available:
    raise Error, Messages.Error.NO_VNC_VIEWER_FOUND


def launch_vncviewer(cmd, host, port, ticket, debug=False):
    """Launch a VNC viewer on host::port with `password'."""

    cmd_passwd = util.which('vncpasswd')
    if cmd_passwd is None:
        raise Error, Messages.Error.NO_SUCH_COMMAND % 'vncpasswd'
    p = Popen([cmd_passwd, "-f"], shell=False, stdin=PIPE, stdout=PIPE)
    password = p.communicate(input=ticket)[0]
    args = [cmd, '%s::%s' % (host, port), '-passwordFile', '/dev/stdin' ]
    pid, pstdin = util.spawn(cmd, args, debug)
    os.write(pstdin, password)
    os.close(pstdin)


def launch_remote_viewer(cmd, host, port, ticket, title, debug=False):
    """Launch the VNC client using the remote-viewer command."""

    # Generate the configuration file:
    config_text = CONFIG_TEMPLATE.format(
        title=title,
        host=host,
        ticket=ticket,
        port=port,
    )
    config_fd, config_path = tempfile.mkstemp()
    with os.fdopen(config_fd, "w") as config_stream:
        config_stream.write(config_text.encode("utf-8"))

    # Run the remote-viewwer command:
    args = ["remote-viewer", config_path]
    util.spawn(cmd, args, debug)
