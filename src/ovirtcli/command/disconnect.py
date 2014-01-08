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
from ovirtcli.state.statemachine import StateMachine

from cli.context import ExecutionContext
from cli.messages import Messages

class DisconnectCommand(OvirtCommand):

    name = 'disconnect'
    description = 'disconnect from oVirt manager'
    helptext = """\
        == Usage ==

        disconnect

        == Description ==

        Disconnect an active connection to oVirt manager, if any. This method
        can be called multiple times. It is not an error to disconnect when
        not connected.
        """

    def execute(self):
        connection = self.context.connection
        if connection is None:
            self.error(
               Messages.Error.NOT_CONNECTED
            )
            return
        try:
            StateMachine.disconnecting()  # @UndefinedVariable
            connection.disconnect()
            self.context.status = ExecutionContext.OK
        except Exception:
            # TODO: consider rollback on disconnect failure (StateMachine.rollback())
            self.context.status = ExecutionContext.COMMAND_ERROR
        finally:
            self.context._clean_settings()
            self.context.connection = None
            StateMachine.disconnected()  # @UndefinedVariable
