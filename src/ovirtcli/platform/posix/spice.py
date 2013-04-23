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
from cli.messages import Messages


def launch_spice_client(host, host_subject, port, secport, ticket, certurl, title,
                        debug=False):
    """Launch the SPICE client."""
    display = os.environ.get('DISPLAY')
    if display is None:
        raise Error, Messages.Error.CANNOT_START_CONSOLE_CLIENT % 'SPICE'
    cmd = util.which('spicec')
    if cmd is None:
        cmd = util.which('/usr/libexec/spicec')
    if cmd is None:
        raise Error, Messages.Error.NO_CONSOLE_FOUND % ('spice', 'spice')
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
    args = ['spicec']
    if cmd.startswith('/usr/libexec'):
        args.extend([host])
        args.extend([str(port)])
        if secport:
            args.extend([str(secport)])
            args.extend(['--ssl-channels', 'smain,sinputs'])
            args.extend(['--ca-file', certfile])
            if host_subject and host_subject != '':
                args.extend(['--host-subject', host_subject])
        args.extend(['-p', ticket])
    else:
        args.extend(['-h', host])
        args.extend(['-p', str(port)])
        if secport:
            args.extend([ '-s', str(secport) ])
            args.extend(['--ca-file', certfile])
            if host_subject and host_subject != '':
                args.extend(['--host-subject', host_subject])
        args.extend(['-w', ticket])
        args.extend(['-t', title])
    pid, pstdin = util.spawn(cmd, args, debug)
