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
from ovirtcli.utils.typehelper import TypeHelper

from ovirtsdk.utils.parsehelper import ParseHelper
from ovirtsdk.infrastructure import brokers
from ovirtcli.utils.methodhelper import MethodHelper

class ActionCommand(OvirtCommand):

    name = 'action'
    description = 'execute an action on an object'
    usage = 'action <type> <action> <id> [options]'
    args_check = 3
    valid_options = [ ('*', str) ]

    helptext0 = """\
        == Usage ==

        action <type> <id> <action> [base identifiers] [attribute options]

        == Description ==

        Executes the an action on an object. This command requires the
        following arguments:

          * type        - The type to operate on
          * id          - The name or id identifying the object
          * action      - The action to take

        For more specific help on the available actions and options, use
        'help action <type> <id>'

        == Available types ==

        The <type> parameter must be one of the following:

          $types

        == Return values ==

        This command will return one of the following statuses. To see the
        exit status of the last command, type 'status'.

          $statuses
        """

    helptext1 = """\
        == Usage ==

        action <type> <id> <action> [object identifiers] [attribute options]

        == Description ==

        Executes the an action on an object. This command requires the
        following arguments:

          * type        - The type to operate on
          * id          - The name or id identifying the object
          * action      - The action to take

        == Available actions ==

        The following actions are available for the specified $type object:

          $actions

        == Object Identifiers ==

        Some objects can only exist inside other objects. For example, a disk
        can only exist in the content of a virtual machine. In this case, one
        or more object identifiers needs to be provided to identify the
        containing object.

        An object identifier is an option of the form '--<type>id <id>'. This
        would identify an object with type <type> and id <id>. See the
        examples section below for a few examples.

        == Attribute Options ==

        The following attribute options are understood. Note: this lists all
        available attribute options for action '$action'.

          $options

        == Examples ==

        This example migrates a vm named "vm0" to the host named "host1":

          $ action vm vm0 migrate --host-name host1

        This example detaches a host nic with id '12345' from host '0':

          $ action nic 12345 detach --hostid 0
    
        == Return values ==

        This command will exit with one of the following statuses. To see the
        exit status of the last command, type 'status'.

          $statuses
        """

    def execute(self):
        """Execute the action command."""
        args = self.arguments
        opts = self.options

        if not (TypeHelper.isKnownType(args[0])):
            self.error('no such type: %s' % args[0])

        scope = '%s:%s' % (ParseHelper.getXmlWrapperType(args[0]), args[2])

        resource = self.get_object(args[0], args[1], self.resolve_base(opts))
        if resource is None:
            self.error('object does not exist: %s/%s', (args[0], args[1]))
        elif hasattr(resource, args[2]):
            method = getattr(resource, args[2])
            try:
#FIXME: support Action obj for actions once parameters supported by RSDL                       
#                        action = self.create_object('Action', opts, scope=scope)
#                        result = method(action)
                result = method()
            except Exception, e:
                self.error(str(e))
            if result.status.state != 'complete':
                self.error('action status: %s' % result.status.state)
        else:
            self.error('no such action: %s' % args[2])
        self.context.formatter.format(self.context, result, scope=scope)

    def show_help(self):
        """Show help for the action command."""
        args = self.arguments
        opts = self.options
        stdout = self.context.terminal.stdout
        types = self._get_actionable_types()
        subst = {}

        if len(args) == 2 and self.is_supported_type(types.keys(), args[0]):
            helptext = self.helptext1

            subst['type'] = args[0]
            subst['id'] = args[1]
            base = self.resolve_base(opts)
            obj = self.get_object(args[0], args[1], base)
            if obj is None:
                self.error('no such %s: %s' % (args[0], args[1]))
            actions = self._get_actions(obj)
            subst['actions'] = self.format_list(actions)
        elif len(args) == 3 and self.is_supported_type(types.keys(), args[0]):
            helptext = self.helptext1

            subst['type'] = args[0]
            subst['id'] = args[1]
            subst['action'] = args[2]

            base = self.resolve_base(self.options)
            obj = self.get_object(args[0], args[1], base)
            if obj is None:
                self.error('no such "%s": "%s"' % (args[0], args[1]))

            actions = self._get_actions(obj)
            if args[2] not in actions:
                self.error('no such action "%s"' % args[2])

            options = self.get_options(method=args[2],
                                       resource=obj,
                                       sub_resource=base)
            subst['actions'] = self.format_list(actions)
            subst['options'] = self.format_list(options, bullet='')
        else:
            helptext = self.helptext0
            subst['types'] = self.format_map(types)

#            scope = '%s:%s' % (type(obj).__name__, args[2])

        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses)
        helptext = self.format_help(helptext, subst)
        stdout.write(helptext)

    def _get_actions(self, obj):
        """INTERNAL: return a list of type actions."""
        actions = []
        exceptions = ['delete', 'update']

        dct = type(obj).__dict__
        if dct and len(dct) > 0:
            for method in dct:
                if method not in exceptions and not method.startswith('_'):
                    actions.append(method)
        return actions

    def _get_actionable_types(self):
        """INTERNAL: return a list of actionable types."""
        types = {}
        exceptions = ['delete', 'update']

        for decorator in TypeHelper.getKnownDecoratorsTypes():
                if not decorator.endswith('s'):
                    dct = getattr(brokers, decorator).__dict__
                    if dct and len(dct) > 0:
                        for method in dct:
                            if method not in exceptions and not method.startswith('_'):
                                self._get_method_params(brokers, decorator, '__init__', types)
                                break
        return types
