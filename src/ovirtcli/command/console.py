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


from ovirtcli.platform import vnc, spice
from ovirtcli.command.command import OvirtCommand

from ovirtsdk.xml import params


class ConsoleCommand(OvirtCommand):

    name = 'console'
    description = 'open a console to a VM'
    args_check = 1

    helptext = """\
        == Usage ==

        console <vm>

        == Description ==

        This opens up a graphical console to a virtual machine. Depending on
        the virtual machine display, this will fire up an external VNC or
        SPICE client.
        """

    def execute(self):
        connection = self.check_connection()
        stdout = self.context.terminal.stdout
        args = self.arguments
        vm = self.get_object('vm', args[0])
        if vm is None:
            self.error('no such vm: %s' % args[0])
        if vm.status.state not in ('powering_up', 'up', 'reboot_in_progress'):
            self.error('vm is not up')
        proto = vm.display.type
        host = vm.display.address
        port = vm.display.port
        secport = vm.display.secure_port
#FIXME: the method should be lower-case in SDK
        action = vm.Ticket()
#        action = connection.action(vm, 'ticket')
        if action.status.state != 'complete':
            self.error('could not set a ticket for the vm')
        ticket = action.ticket.value_
        debug = self.context.settings['cli:debug']
        if proto == 'vnc':
            vnc.launch_vnc_viewer(host, port, ticket, debug)
        elif proto == 'spice':
            certurl = 'https://%s:%s/ca.crt' % (connection.host, connection.port)
            spice.launch_spice_client(host, port, secport, ticket, certurl,
                                      vm.name, debug)
        else:
            self.error('unsupported display protocol: %s' % proto)
