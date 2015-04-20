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
import types
from cli.messages import Messages

class ActionCommand(OvirtCommand):

    name = 'action'
    description = 'execute an action on an object'
    usage = 'action <type> <id> <action> [parent identifiers] [command options]'
    args_check = 3
    valid_options = [ ('*', str) ]

    helptext0 = """\
        == Usage ==

        action <type> <id> <action> [parent identifiers] [command options]

        Note that when using auto-completion it may be necessary to know
        the parent identifiers of the object in order to determine the
        available actions, so the following syntax, with the action
        after the parent identifiers, is also accepted:

        action <type> <id> [parent identifiers] <action> [command options]

        == Description ==

        Executes the an action on an object. This command requires the
        following arguments:

          * type        - The type to operate on
          * id          - The name or id identifying the object
          * action      - The action to take

        For more specific help on the available actions and options, use
        'help action <type> <id>'

        == Supported Help formats ==

        - This help will list all available attribute options for given resource
          
          * format      - help action type id
          * example     - help action vm myvm

        - This help will list all available attribute options for specific action on given resource
        
          * format      - help action type id action_name
          * example     - help action vm myvm start
        
        - This help will list all available attribute options for specific subresource 
        
          * format      - help action resource resource_name --parent-subresource-identifier mysubresource
          * example     - help action nic bond0 --parent-host-identifier myhost
        
        - This help will display all available attribute options for specific action on given subresource

          * format      - help action action_name resource resource_name --parent-subresource-identifier mysubresource
          * example     - help action attach nic bond0 --parent-host-identifier myhost

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

        action <type> <id> <action> [parent identifiers] [command options]

        Note that when using auto-completion it may be necessary to know
        the parent identifiers of the object in order to determine the
        available actions, so the following syntax, with the action
        after the parent identifiers, is also accepted:

        action <type> <id> [parent identifiers] <action> [command options]

        == Description ==

        Executes the an action on an object. This command requires the
        following arguments:

          * type        - The type to operate on
          * id          - The name or id identifying the object
          * action      - The action to take

        == Available actions ==

        The following actions are available for the specified $type object:

          $actions

        == Collection based option format ==

          * [--x-y: collection]
            {
              [y.a: string]
              [y.b: string]
              [y.c: string]
            }

          e.g:

          --x-y "y.a=a1,y.b=b1,y.c=c1"
          --x-y "y.a=a2,y.b=b2,y.c=c2"
          ...

          where a, b, c are option properties and aN, bN, cN is actual user's data

        == Object Identifiers ==

        Some objects can exist inside other objects. For example, a disk can
        exist in the content of a virtual machine. In this case, one or more
        parent object identifier options need to be provided to identify the
        parent object.

        An parent object identifier is an option of the form
        '--parent-<type>-identifier <id>' or '--parent-<type>-name <name>'. This
        would identify a parent object with type <type> and id <id> or name
        <name>. See the examples section below for a few examples.

        == Attribute Options ==

        The following attribute options are understood. Note: this lists all
        available attribute options for action '$action'.

          $options

        == Examples ==

        - This example starts a vm named "myvm" with few optional parameters:

          $ action vm iscsi_desktop start --vm-display-type vnc --vm-cpu-topology-sockets 2 --vm-cpu-topology-cores 2

        - This example detaches a host nic with id 'mynic' from host 'myhost':

          $ action nic mynic detach --parent-host-name myhost
    
        == Return values ==

        This command will exit with one of the following statuses. To see the
        exit status of the last command, type 'status'.

          $statuses
        """

    def execute(self):
        """Execute the action command."""
        args = self.arguments
        opts = self.options

        if not (TypeHelper.isKnownType(args[0])) and \
           ParseHelper.getXmlType(args[0]) == None:
            self.error(
                       Messages.Error.NO_SUCH_TYPE % args[0]
            )

        # scope = '%s:%s' % (ParseHelper.getXmlWrapperType(args[0]), args[2])
        actionable_types = TypeHelper.get_actionable_types(
                       expendNestedTypes=True,
                       groupOptions=True
        )

        resource = self.get_object(
                       args[0],
                       args[1],
                       self.resolve_base(opts),
                       context_variants=actionable_types[args[0]]
        )

        if resource is None:
            self.error(
                   Messages.Error.NO_SUCH_OBJECT % (args[0], args[1])
            )
        elif hasattr(resource, args[2]) and \
             type(getattr(resource, args[2])) == types.MethodType:
            try:
                result = self.execute_method(resource, args[2], opts)
            except Exception, e:
                self.error(str(e))
            if result.status.state == 'failed':
                self.error(
                       Messages.Info.ACTION_STATUS % result.status.state
                )
        else:
            self.error(
                   Messages.Error.NO_SUCH_ACTION % args[2]
            )
        self.context.formatter.format(self.context, result)

    def show_help(self):
        """Show help for the action command."""
        args = self.arguments
        opts = self.options
        types = TypeHelper.get_actionable_types(
                                expendNestedTypes=True,
                                groupOptions=True
        )
        subst = {}

        if not args or self.is_supported_type(types.keys(), args[0]):
            if len(args) == 2 and len(opts) == 2:
                helptext = self.helptext1

                subst['type'] = args[0]
                subst['id'] = args[1]

                base = self.resolve_base(self.options)
                obj = self.get_object(
                              args[0],
                              args[1],
                              base,
                              context_variants=types[args[0]]
                )
                if obj is None:
                    self.error(
                           Messages.Error.NO_SUCH_OBJECT % (args[1], args[1])
                    )
                actions = self._get_action_methods(obj)
                subst['actions'] = self.format_list(actions)

            if len(args) == 3 and len(opts) == 2:
                helptext = self.helptext1

                subst['type'] = args[0]
                subst['id'] = args[1]
                subst['action'] = args[0]

                base = self.resolve_base(self.options)
                obj = self.get_object(
                              args[1],
                              args[2],
                              base,
                              context_variants=types[args[0]]
                )
                if obj is None:
                    self.error(
                       Messages.Error.NO_SUCH_OBJECT % (args[0], args[1])
                    )

                actions = self._get_action_methods(obj)
                if args[0] not in actions:
                    self.error(
                           Messages.Error.NO_SUCH_ACTION % args[2]
                    )

                options = self.get_options(
                           method=args[0],
                           resource=obj,
                           context_variants=types[args[0]]
                )
                subst['actions'] = self.format_list(actions)
                subst['options'] = self.format_list(options, bullet='', sort=False)

            elif len(args) == 1:
                helptext = self.helptext0
                subst['types'] = self.format_map({args[0]:types[args[0]]})
                subst['type'] = args[0]

            elif len(args) == 2:
                helptext = self.helptext1

                subst['type'] = args[0]
                subst['id'] = args[1]
                base = self.resolve_base(opts)
                obj = self.get_object(
                              args[0],
                              args[1],
                              base,
                              context_variants=types[args[0]]
                )
                if obj is None:
                    self.error(
                       Messages.Error.NO_SUCH_OBJECT % (args[0], args[1])
                )
                actions = self._get_action_methods(obj)
                subst['actions'] = self.format_list(actions)

            elif len(args) == 3:
                helptext = self.helptext1

                subst['type'] = args[0]
                subst['id'] = args[1]
                subst['action'] = args[2]

                base = self.resolve_base(self.options)
                obj = self.get_object(
                          args[0],
                          args[1],
                          base,
                          context_variants=types[args[0]]
                )
                if obj is None:
                    self.error(
                       Messages.Error.NO_SUCH_OBJECT % (args[0], args[1])
                    )

                actions = self._get_action_methods(obj)
                if args[2] not in actions:
                    self.error(Messages.Error.NO_SUCH_ACTION % args[2])

                options = self.get_options(
                           method=args[2],
                           resource=obj,
                           sub_resource=base,
                           context_variants=types[args[0]]
                )
                subst['actions'] = self.format_list(actions)
                subst['options'] = self.format_list(options, bullet='', sort=False)

            else:
                helptext = self.helptext0
                subst['types'] = self.format_map(types)

    #            scope = '%s:%s' % (type(obj).__name__, args[2])

            statuses = self.get_statuses()
            subst['statuses'] = self.format_list(statuses)
            helptext = self.format_help(helptext, subst)
            self.write(helptext)
