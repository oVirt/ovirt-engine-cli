#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


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
