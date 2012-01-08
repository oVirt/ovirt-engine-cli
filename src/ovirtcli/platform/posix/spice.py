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
import urllib

from cli.error import Error
from ovirtcli.platform import util


def launch_spice_client(host, port, secport, ticket, certurl, title,
                        debug=False):
    """Launch the SPICE client."""
    display = os.environ.get('DISPLAY')
    if display is None:
        raise Error, '$DISPLAY not set, cannot start a SPICE client'
    cmd = util.which('spicec')
    if cmd is None:
        cmd = util.which('/usr/libexec/spicec')
    if cmd is None:
        raise Error, 'spicec: command not found'
    certdir = os.path.join(util.get_home_dir(), '.spicec')
    try:
        os.stat(certdir)
    except OSError:
        os.mkdir(certdir)
    certfile = os.path.join(certdir, 'spice_truststore.pem')
    try:
        os.stat(certfile)
    except OSError:
        certtmp = '%s.%d-tmp' % (certfile, os.getpid())
        urllib.urlretrieve(certurl, certtmp)
        os.rename(certtmp, certfile)
    if cmd.startswith('/usr/libexec'):
        args = [ 'spicec', host, str(port), str(secport), '--ssl-channels',
                 'smain,sinputs', '--ca-file', certfile, '-p', ticket ]
    else:
        args = [ 'spicec', '-h', host, '-p', str(port), '-s', str(secport),
                 '-w', ticket, '-t', title ]
    pid, pstdin = util.spawn(cmd, args, debug)
