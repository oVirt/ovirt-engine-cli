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


import logging

from ovirtcli.platform import ssh, expect
from ovirtcli.command.command import OvirtCommand
from ovirtcli.command.getkey_cmd import dumpkey_function


class GetKeyCommand(OvirtCommand):

    name = 'getkey'
    description = 'dump private ssh key'
    args_check = 0

    helptext = """\
        == Usage ==

        getkey

        == Description ==

        This commands dumps the private ssh key that oVirt manager is using to
        communicate with the hypervisor nodes. It can be used to connect via
        ssh to hypervisor nodes.
        """

    def execute(self):
        terminal = self.context.terminal
        connection = self.check_connection()
        host = connection.host
        terminal.stdout.write('Enter password for root@%s: ' % host)
        terminal.stdout.flush()
        terminal.set_echo(False)
        passwd = terminal.stdin.readline()
        terminal.set_echo(True)
        terminal.stdout.write('\n')
        if not passwd:
            terminal.stdout.write('No password entered\n')
            return
        cmd = ssh.create_password_login_command('root', host)
        logging.debug('ssh command is: %s' % cmd)
        child = expect.spawn(cmd, timeout=4)
        child.expect('password:')
        child.send(passwd + '\n')
        ix = child.expect(['# ', 'password:'])
        if ix == 1:
            terminal.stdout.write('Illegal password for root@%s\n' % host)
            return
        child.send(dumpkey_function)
        child.expect('# ')
        child.send('dumpkey /etc/pki/rhevm/.keystore rhevm mypass\n')
        child.expect('-----BEGIN PRIVATE KEY-----\r\n')
        terminal.stdout.write(child.match.group(0))
        child.expect('-----END PRIVATE KEY-----\r\n')
        terminal.stdout.write(child.before)
        terminal.stdout.write(child.match.group(0))
        child.send('exit\n')
        child.expect(expect.EOF)
        child.close()
