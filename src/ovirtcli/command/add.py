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


from cli.messages import Messages
from ovirtcli.command.command import OvirtCommand
from ovirtcli.utils.typehelper import TypeHelper

class AddCommand(OvirtCommand):

    name = 'add'
    aliases = ('add',)
    description = 'creates a new object or adds existent'
    args_check = 1
    valid_options = [ ('*', str) ]

    helptext0 = """\
        == Usage ==

        add <type> [parent identifiers] [command options]

        == Description ==

        Creates a new object or adds existent

        == Supported Help formats ==

        - This help will list all available attribute options for given resource creation
          
          * format      - help add resource_name
          * example     - help add vm

        - This help will list all available attribute options for given subresource creation
          
          * format      - help add subresource_name --parent-resource-identifier xxx
          * example     - help add disk --parent-vm-identifier myvm

        == Available Types ==

        The following types of objects can be added:

          $types

        == Base Identifiers ==

        Some objects can exist inside other objects. For example, a disk can
        exist in the content of a virtual machine. In this case, one or more
        object identifier options need to be provided to identify the
        containing object.

        An object identifier is an option of the form
        '--parent-<type>-identifier <id>' or '--parent-<type>-name <name>'. This
        would identify an object with type <type> and id <id> or name <name>.
        See the examples section below for a few examples.

        == Attribute Options ==

        Attribute options specify values for attributes of the to be created
        object.

        Attributes for the new object can be specified in one of two ways.

          * Using command-line options. For example, "--description foo"
            would add the object with a description of "foo".
          * By providing pre-formatted input, in the format specified by the
            'input_format' configuration variable. In this case the input
            needs to be provided using the '<<' input redirection operator.

        Type 'help add <type>' to see an overview of which attributes are
        available for a given type.
          
        == Examples ==

        - This example create a new virtual machine in the Default cluster based on the
          Blank template:

          $ add vm --name myvm --template-name iscsi_desktop_tmpl --cluster-name Default_iscsi
                      
        - This example create vm nic:

          $ add nic --parent-vm-name cli_vm3 --network-name engine --name test


        == Return Values ==

          $statuses
        """

    helptext1 = """\
        == Usage ==

        add <type> [parent identifiers] [command options]

        == Description ==

        Creates a new object or adds existent with type $type. See 'help add' for generic
        help on creating objects.

        == Attribute Options ==

        The following options are available for objects with type $type:

          $options

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

        == Return Values ==

          $statuses
        """

    def execute(self):
        """Execute the "add" command."""
        args = self.arguments
        opts = self.options
        base = self.resolve_base(opts)
        typ = TypeHelper.to_plural(args[0])
        collection = None
        typs = self.get_singular_types(method='add', typ=args[0])

        if base:
            if hasattr(base, typ):
                collection = getattr(base, typ)
        else:
            connection = self.check_connection()
            if hasattr(connection, typ):
                collection = getattr(connection, typ)

        if collection != None:
            result = self.execute_method(collection, 'add', opts)
            self.context.formatter.format(self.context, result)
        else:
            err_str = Messages.Error.CANNOT_CREATE
            if typs:
                err_str = err_str + \
                (Messages.Info.POSSIBALE_ARGUMENTS_COMBINATIONS % str(typs))
            self.error(
                   err_str % (args[0], typ)
            )


    def show_help(self):
        """Show help for "add"."""
        args = self.arguments
        opts = self.options
        types = self.get_singular_types(method='add')
        subst = {}
        if len(args) == 0:
            helptext = self.helptext0
            subst['types'] = self.format_map(types)
        elif len(args) == 1:
            if self.is_supported_type(types.keys(), args[0]):
                helptext = self.helptext1
                params_list = self.get_options(
                       method='add',
                       resource=args[0],
                       sub_resource=self.resolve_base(opts),
                       context_variants=types[args[0]]
                )
                subst['options'] = self.format_list(params_list, sort=False)
                subst['type'] = args[0]
        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses)
        helptext = self.format_help(helptext, subst)
        self.write(helptext)
