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
import re
import tempfile
import urllib

from cli.error import Error
from ovirtcli.platform import util
from cli.messages import Messages


# Template to generate the remote viewer configuration file:
CONFIG_TEMPLATE = u"""\
[virt-viewer]
type=spice
title={title}:%d - Press SHIFT+F12 to Release Cursor
host={host}
port={port}
tls-port={secport}
password={ticket}
fullscreen=0
enable-smartcard=0
enable-usb-autoshare=1
delete-this-file=1
usb-filter=-1,-1,-1,-1,0
tls-ciphers=DEFAULT
host-subject={host_subject}
toggle-fullscreen=shift+f11
release-cursor=shift+f12
secure-attention=ctrl+alt+del
secure-channels=main;inputs;cursor;playback;record;display;usbredir;smartcard
ca={ca_text}
"""


def launch_spice_client(host, host_subject, port, secport, ticket, url,
                        title, debug=False):
    """Launch the SPICE client."""

    # Check that there is a X display available:
    display = os.environ.get('DISPLAY')
    if display is None:
        raise Error, Messages.Error.CANNOT_START_CONSOLE_CLIENT % 'SPICE'

    # Download and save the CA certificate tot he directory and file where the
    # clients expect it:
    ca_dir = os.path.join(util.get_home_dir(), '.spicec')
    try:
        os.stat(ca_dir)
    except OSError:
        os.mkdir(ca_dir)
    ca_file = os.path.join(ca_dir, 'spice_truststore.pem')
    try:
        os.stat(ca_file)
    except OSError:
        ca_text = download_ca_certificate(url)
        with open(ca_file, "w") as ca_stream:
            ca_stream.write(ca_text)

    # Try to use remote viewer:
    cmd = util.which("remote-viewer")
    if cmd is not None:
        launch_remote_viewer(cmd, host, host_subject, port, secport, ticket,
                             title, ca_file, debug)
        return

    # Try to use spicec (this is older, so we try only if remote-viewer isn't
    # available):
    cmd = util.which('spicec')
    if cmd is None:
        cmd = util.which('/usr/libexec/spicec')
    if cmd is not None:
        launch_spicec(cmd, host, host_subject, port, secport, ticket,
                      title, ca_file, debug)
        return

    # No luck, no known command is available:
    raise Error, Messages.Error.NO_SPICE_VIEWER_FOUND


def launch_spicec(cmd, host, host_subject, port, secport, ticket,
                  title, ca_file, debug=False):
    """Launch the SPICE client using the spicec command."""

    args = ['spicec']
    if cmd.startswith('/usr/libexec'):
        args.extend([host])
        if port is not None:
            args.append([str(port)])
        else:
            args.extend(["0"])
        if secport:
            args.extend([str(secport)])
            args.extend(['--ssl-channels', 'smain,sinputs'])
            args.extend(['--ca-file', ca_file])
            if host_subject and host_subject != '':
                args.extend(['--host-subject', host_subject])
        args.extend(['-p', ticket])
    else:
        args.extend(['-h', host])
        if port is not None:
            args.extend(['-p', str(port)])
        if secport:
            args.extend([ '-s', str(secport) ])
            args.extend(['--ca-file', ca_file])
            if host_subject and host_subject != '':
                args.extend(['--host-subject', host_subject])
        args.extend(['-w', ticket])
        args.extend(['-t', title])
    util.spawn(cmd, args, debug=True)


def launch_remote_viewer(cmd, host, host_subject, port, secport, ticket,
                         title, ca_file, debug=False):
    """Launch the SPICE client using the remote-viewer command."""

    # Load the CA certificate:
    with open(ca_file, "r") as ca_stream:
        ca_text = ca_stream.read()

    # Generate the configuration file:
    config_text = CONFIG_TEMPLATE.format(
        title=title,
        host=host,
        ticket=ticket,
        port=port,
        secport=secport,
        host_subject=host_subject,
        ca_text=ca_text.replace("\n", "\\n"),
    )
    config_fd, config_path = tempfile.mkstemp()
    with os.fdopen(config_fd, "w") as config_stream:
        config_stream.write(config_text.encode("utf-8"))

    # Run the remote-viewwer command:
    args = ["remote-viewer", config_path]
    util.spawn(cmd, args, debug)


def download_ca_certificate(url):
    """Downloads the CA certificate from the engine."""

    ca_url = re.sub("^https?://([^/]+)/.*", "http://\\1/ca.crt", url)
    ca_file = None
    try:
        ca_fd, ca_file = tempfile.mkstemp()
        urllib.urlretrieve(ca_url, ca_file)
        with os.fdopen(ca_fd, "r") as ca_stream:
            ca_text = ca_stream.read()
        return ca_text
    finally:
        if ca_file is not None:
            os.remove(ca_file)
