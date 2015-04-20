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

import re

from cli.messages import Messages
from ovirtcli.command.command import OvirtCommand
from ovirtcli.utils.typehelper import TypeHelper


class ShowCommand(OvirtCommand):

    name = 'show'
    description = 'show one object'
    args_check = lambda self, x: len(x) > 0
    valid_options = [ ('*', str) ]

    helptext = """\
        == Usage ==
    
        show <type> <id|name> [parent identifiers] [command options]

        == Description ==

        Retrieve an object and display information about it. The following
        arguments are required:

          * type        The type of object to retrieve
          * id          The object identifier
          * name        The object name

        Objects can be identified by their name and by their unique id.

        == Supported Help formats ==

        - This help will show all available attribute options for showing 
          resource
          
          * format      - help show type
          * example     - help show vm

        == Available Types ==

        The <type> parameter must be one of the following.

          $types

        == Object Identifiers ==

	Some objects can exist inside other objects. For example, a disk can
        exist in the content of a virtual machine. In this case, one or more
        object identifier options need to be provided to identify the
        containing object.

        An object identifier is an option of the form '--parent-<type>-identifier
        <id>' or '--parent-<type>-name <name>'. This would identify an object with
        type <type> and id <id> or name <name>. See the examples section below
        for a few examples.

        == Examples ==

        - This example shows information about the virtual machine "myvm"

          $ show vm myvm

        - This example shows information about the disk named 'disk1' of the 
          virtual machine with identifier
          "a71ff45c-d2d7-44d7-98e6-be06f5a82016":

          $ show disk disk1 --parent-vm-identifier a71ff45c-d2d7-44d7-98e6-be06f5a82016

        - This example shows information about the nic named 'nic1' of the 
          virtual machine with name "myvm":

          $ show nic nic1 --parent-vm-name myvm

        == Return values ==

        This command will exit with one of the following statuses. To see the
        exit status of the last command, type 'status'.

          $statuses
        """

    helptext1 = """\
        == Usage ==

        - show <type>
            
        - show <type> <id> [parent identifiers] [command options]

        == Description ==

        Shows an object by type '$type'. See 'help show' for generic
        help on showing objects.

        == Attribute Options ==

        The following options are available for objects with type '$type':

          $options

        == Return values ==

        This command will exit with one of the following statuses. To see the
        exit status of the last command, type 'status'.

          $statuses
        """

    def execute(self):
        """Execute "show"."""
        args = self.arguments
        opts = self.options

        # Raise an error if object identifier xxx is not specified #855750
        # e.g:
        # show vm xxx
        # show disk xxx --parent-vm-identifier yyy
        # show disk xxx --parent-vm-name zzz
        if len(args) < 2 and (
                          len(opts) == 0 or
                          (
                           len(opts) == 1
                           and
                           re.search(r"-(identifier|name)$", opts.keys()[0])
                          )):
            self.error(
              Messages.Error.NO_IDENTIFIER_OR_NAME % args[0]
            )

        types = self.get_singular_types(method='get')
        obj = self.get_object(
              typ=args[0],
              obj_id=args[1] if len(args) > 1
                             else None,
              base=self.resolve_base(opts),
              opts=opts,
              context_variants=types[args[0]]
        )

        if not (obj):
            self.error(
               Messages.Error.NO_SUCH_OBJECT %
               (args[0], args[1] if len(args) > 1
                                 else self.get_object_id(opts.values())
                                      if opts else '')
            )
        self.context.formatter.format(self.context, obj)

    def get_object_id(self, opts_values):
        """Get Object Identifier."""
        if len(opts_values) == 1:
            return opts_values[0]
        return opts_values

    def show_help(self):
        """Show help for "show"."""
        self.check_connection()
        args = self.arguments
        opts = self.options

        subst = {}
        types = self.get_singular_types(method='get')

        if not args or self.is_supported_type(types.keys(), args[0]):

            subst['types'] = self.format_map(types)

            statuses = self.get_statuses()
            subst['statuses'] = self.format_list(statuses)

            if len(args) == 1:
                helptext = self.helptext1
                params_list = self.get_options(
                       method='get',
                       resource=TypeHelper.to_singular(args[0]),
                       sub_resource=self.resolve_base(opts),
                       context_variants=types[args[0]]
                )
                subst['options'] = self.format_list(params_list)
                subst['type'] = args[0]
            elif len(args) == 2:
                helptext = self.helptext1

                subst['type'] = args[0]
                subst['id'] = args[1]
                base = self.resolve_base(opts)
                obj = self.get_object(args[0], args[1], base)
                if obj is None:
                    self.error(
                       Messages.Error.NO_SUCH_OBJECT % (args[0], args[1])
                    )

                params_list = self.get_options(
                       method='get',
                       resource=obj,
                       sub_resource=base,
                       context_variants=types[args[0]]
                )
                subst['options'] = self.format_list(params_list)

            else:
                helptext = self.helptext

            helptext = self.format_help(helptext, subst)
            self.write(helptext)
