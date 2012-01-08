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


from ovirtcli.command.command import OvirtCommand


class PingCommand(OvirtCommand):

    name = 'ping'
    description = 'test the connection'
    helptext = """\
        == Usage ==

        ping

        == Description ==

        Test the connection to the oVirt manager. This command will go out to
        the oVirt manager and retrieve a remote resource. If it succeeds, you
        know that the URL, username and password are working.
        """

    def execute(self):
        connection = self.check_connection()
        stdout = self.context.terminal.stdout
        try:
            connection.vms.list()
#TODO: support this
#            connection.ping()
#        except Error:
        except Exception:
            stdout.write('error: could NOT reach oVirt manager\n')
        else:
            stdout.write('success: oVirt manager could be reached OK\n')
