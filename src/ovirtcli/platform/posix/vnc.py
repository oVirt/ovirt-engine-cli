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
from cli.messages import Messages
from subprocess import Popen, PIPE


def launch_vnc_viewer(host, port, ticket, debug=False):
    """Launch a VNC viewer on host::port with `password'."""
    display = os.environ.get('DISPLAY')
    if display is None:
        raise Error, Messages.Error.INVALID_ENV_MODE_FOR_CONSOLE % 'vnc'
    cmd = util.which('vncviewer')
    if cmd is None:
        raise Error, Messages.Error.NO_CONSOLE_FOUND % ('vnc', 'vnc')
    cmd_passwd = util.which('vncpasswd')
    if cmd_passwd is None:
        raise Error, Messages.Error.NO_SUCH_COMMAND % 'vncpasswd'
    p = Popen([cmd_passwd, "-f"], shell=False, stdin=PIPE, stdout=PIPE)
    password = p.communicate(input=ticket)[0]
    args = [cmd, '%s::%s' % (host, port), '-passwordFile', '/dev/stdin' ]
    pid, pstdin = util.spawn(cmd, args, debug)
    os.write(pstdin, password)
    os.close(pstdin)
