
from ovirtcli.command.command import OvirtCommand
from ovirtcli.utils.typehelper import TypeHelper

class CreateCommand(OvirtCommand):

    name = 'create'
    aliases = ('add',)
    description = 'create a new object'
    args_check = 1
    valid_options = [ ('*', str) ]

    helptext0 = """\
        == Usage ==

        create <type> [base identifiers] [attribute options]

        == Description ==

        Create a new object with type <type>.

        == Available Types ==

        The following types of objects can be created:

          $types

        == Base Identifiers ==

        Some objects can only be created inside other objects. For example a
        disk can only be created inside a virtual machine. In this case, one
        or more base identifier options need to be given to identify the
        containing object. These options have the form --<type>id <id>.

        == Attribute Options ==

        Attribute options specifiy values for attributes of the to be created
        object.

        Attributes for the new object can be specified in one of two ways.

          * Using command-line options. For example, "--description foo"
            would create the object with a description of "foo".
          * By providing pre-formatted input, in the format specified by the
            'input_format' configuration variable. In this case the input
            needs to be provided using the '<<' input redirection operator.

        Type 'help create <type>' to see an overview of which attributes are
        available for a given type.

        == Examples ==

        This create a new virtual machine in the Default cluster based on the
        Blank template:

          $ create vm --name myvm --memory 512 --type SERVER \\
                      --cluster Default --template Blank

        This example does the same but now using pre-formatted input:

          $ create vm << EOM
          > <vm>
          >   <name>myvm</name>
          >   <memory>512000000</memory>
          >   <type>SERVER</type>
          >   <cluster><name>Default</name></cluster>
          >   <template><name>Blank</name></template>
          > </vm>
          > EOM

        == Return Values ==

          $statuses
        """

    helptext1 = """\
        == Usage ==

        create <type> [base identifiers] [attribute options]

        == Description ==

        Create a new object with type $type. See 'help create' for generic
        help on creating objects.

        == Attribute Options ==

        The following options are available for objects with type $type:

          $options

        == Return Values ==

          $statuses
        """

    def execute(self):
        """Execute the "create" command."""
        args = self.arguments
        opts = self.options
        connection = self.check_connection()
        base = self.resolve_base(opts)

        if not (TypeHelper.isKnownType(args[0])):
            self.error('no such type: %s' % args[0])

        result = getattr(base if base is not None else connection,
                         args[0] + 's').add(self.create_object(args[0],
                                                               opts))

        self.context.formatter.format(self.context, result)

    def show_help(self):
        """Show help for "create"."""
        args = self.arguments
        opts = self.options
        connection = self.check_connection()
        stdout = self.context.terminal.stdout
        subst = {}
        if len(args) == 0:
            helptext = self.helptext0
            types = self.get_singular_types()
            subst['types'] = self.format_list(types)
        elif len(args) == 1:
#            info = schema.type_info(args[0])
#FIXME:
            info = None
            if info is None:
                self.error('unknown type: %s' % args[0])
            base = self.resolve_base(opts)
            methods = connection.get_methods(info[1], base=base)
            if 'POST' not in methods:
                self.error('type cannot be created: %s' % args[0])
            helptext = self.helptext1
            subst['type'] = args[0]
            options = self.get_options(info[0], 'C')
            subst['options'] = self.format_list(options)
        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses)
        helptext = self.format_help(helptext, subst)
        stdout.write(helptext)
