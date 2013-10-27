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
from ovirtcli.infrastructure.settings import OvirtCliSettings
from cli.messages import Messages


class PingCommand(OvirtCommand):

    name = 'ping'
    description = 'test the connection'
    helptext = """\
        == Usage ==

        ping

        == Description ==

        Test the connection to the %s manager. This command will go out to
        the %s manager and retrieve a remote resource. If it succeeds, you
        know that the URL, username and password are OK (note: there are few 
        optional parameters that might be needed for establishing connection).
        """ % (OvirtCliSettings.PRODUCT , OvirtCliSettings.PRODUCT)

    def execute(self):
        connection = self.check_connection()
        try:
            connection.test(throw_exception=True)
        except Exception, e:
            self.write('\n' + str(e) + '\n')
            self.error(
                   Messages.Error.CANNOT_CONNECT_TO_BACKEND
                   %
                   OvirtCliSettings.PRODUCT
            )
        else:
            self.write(
                   Messages.Info.SUCESS_CONNECT_TO_BACKEND
            )
