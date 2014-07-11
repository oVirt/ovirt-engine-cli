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


from ovirtcli.platform import vnc, spice
from ovirtcli.command.command import OvirtCommand
from cli.messages import Messages


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
        self.check_connection()
        args = self.arguments
        CONSOLE_STATES = ['powering_up', 'up', 'reboot_in_progress']
        host_subject = ''

        vm = self.get_object('vm', args[0])
        if vm is None:
            self.error(
               Messages.Error.NO_SUCH_OBJECT % ('vm', args[0])
            )
        if vm.status.state not in CONSOLE_STATES:
            self.error(
               Messages.Error.CANNOT_CONNECT_TO_VM_DUE_TO_INVALID_STATE +
               Messages.Info.POSSIBLE_VM_STATES_FOR_CONSOLE % str(CONSOLE_STATES)
           )

        host_addr = vm.display.address
        proto = vm.display.type_
        port = vm.display.port
        secport = vm.display.secure_port
        action = vm.ticket()

        if action.status.state != 'complete':
            self.error(
               Messages.Error.CANNOT_SET_VM_TICKET
            )
        ticket = action.ticket.value
        debug = self.context.settings['cli:debug']

        if proto == 'vnc':
            vnc.launch_vnc_client(host_addr, port, ticket, vm.name, debug)
        elif proto == 'spice':
            if vm.host and vm.host.id:
                host = self.get_object('host', vm.host.id)
                if host:
                    if hasattr(host, 'certificate') and host.certificate:
                        if host.certificate.subject:
                            host_subject = host.certificate.subject
                        else:
                            self.warning(
                                 Messages.Warning.CANNOT_FETCH_HOST_CERT_SUBJECT
                            )
                    else:
                        self.warning(
                             Messages.Warning.CANNOT_FETCH_HOST_CERT_SUBJECT_LEGACY_SDK
                        )
            if host_subject == '':
                    self.warning(
                         Messages.Warning.HOST_IDENTITY_WILL_NOT_BE_VALIDATED
                    )
            spice.launch_spice_client(
                          host_addr,
                          host_subject,
                          port, secport,
                          ticket,
                          self.context.url,
                          vm.name,
                          debug
            )
        else:
            self.error(
                   Messages.Error.INVALID_DISPLAY_PROTOCOL % proto
            )
