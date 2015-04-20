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
from cli.messages import Messages


class UpdateCommand(OvirtCommand):

    name = 'update'
    description = 'update an object'
    args_check = 2
    valid_options = [ ('*', str) ]

    helptext = """\
        == Usage ==

        update <type> <id> [parent identifiers] [command options]

        == Description ==

        Update an existing object. This command requires the following
        arguments:

          * type        The type of object to update.
          * id          The identifier of the object to update

        == Supported Help formats ==

        - This help will list all available attribute options for given resource update
          
          * format      - help update type
          * example     - help update vm

        - This help will list all available attribute options for given subresource update
          
          * format      - help update type --parentid
          * example     - help update disk --vm-name myvm

        == Available Types ==

        The following object types are available:

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

        Attribute options specifiy values for attributes of the object that is
        to be updated.

        Type 'help update <type>' to see an overview of which attributes are
        available for a specific type.

        == Examples ==

        - This example updates a virtual machine with name "myvm", setting new 
          description and amount of monitors.

          $ update vm myvm --display-monitors 1 --description test1

        - This example updates a virtual machine disk with name "mydisk", setting 
          "bootable" to true.

          $ update disk "mydisk" --parent-vm-name "myvm" --bootable true

        == Return Values ==

          $statuses
        """

    helptext1 = """\
        == Usage ==

        update <type> <id> [parent identifiers] [command options]

        == Description ==

        Update an existing object. This command requires the following
        arguments:

          * type        The type of object to update.
          * id          The identifier of the object to update

        See 'help update' for generic help on creating objects.

        == Attribute Options ==

        The following options are available for objects with type '$type':

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
        """Execute the "update" command."""
        args = self.arguments
        opts = self.options

        typs = TypeHelper.get_types_containing_method(
                      'update',
                       expendNestedTypes=True,
                       groupOptions=True
        )

        resource = self.get_object(
                       args[0], args[1],
                       self.resolve_base(opts),
                       context_variants=typs[args[0]]
        )

        if resource is None:
            self.error(
               Messages.Error.NO_SUCH_OBJECT % (args[0], args[1])
            )
        elif hasattr(resource, 'update'):
            obj = self.update_object_data(self.__create_set_superclass(resource), opts)
            result = self.execute_method(obj, 'update', opts)
        else:
            self.error(
               Messages.Error.OBJECT_IS_IMMUTABLE % (args[0], args[1])
            )
        self.context.formatter.format(self.context, result)

    def __create_set_superclass(self, resource):
        """Create an instance of param object."""
        param_obj = type(resource.superclass).factory()
        if hasattr(param_obj, 'id'):
            setattr(param_obj, 'id', getattr(resource, 'id'))
        resource.superclass = param_obj
        return resource

    def show_help(self):
        """Show help for "update"."""

        self.check_connection()
        args = self.arguments
        opts = self.options

        subst = {}
        types = TypeHelper.get_types_containing_method(
               'update',
               expendNestedTypes=True,
               groupOptions=True
        )
        subst['types'] = self.format_map(types)
        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses)

        if len(args) > 0 and self.is_supported_type(types.keys(), args[0]):
            if len(args) == 2:
                base = self.resolve_base(self.options)
                obj = self.get_object(
                          args[0], args[1],
                          base,
                          context_variants=types[args[0]]
                )
                if obj is None:
                    self.error(
                          Messages.Error.NO_SUCH_OBJECT % (args[0], args[1])
                    )
                helptext = self.helptext1
                params_list = self.get_options(
                           method='update',
                           resource=obj,
                           sub_resource=base,
                           context_variants=types[args[0]]
                )
                subst['options'] = self.format_list(params_list)
                subst['type'] = args[0]

            elif len(args) == 1 and len(opts) == 2:
                helptext = self.helptext1

                subst['type'] = args[0]

                options = self.get_options(
                           method='update',
                           resource=args[0],
                           sub_resource=self.resolve_base(self.options),
                           context_variants=types[args[0]]
                )
                subst['options'] = self.format_list(options)
                subst['type'] = args[0]
            elif len(args) == 1:
                helptext = self.helptext
                subst['type'] = args[0]
                subst['types'] = self.format_map({args[0]:types[args[0]]})
            else:
                helptext = self.helptext
        else:
            helptext = self.helptext

        helptext = self.format_help(helptext, subst)
        self.write(helptext)
