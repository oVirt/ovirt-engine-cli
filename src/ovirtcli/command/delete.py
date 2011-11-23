

from ovirtcli.command.command import OvirtCommand
from ovirtcli.utils.typehelper import TypeHelper


class DeleteCommand(OvirtCommand):

    name = 'delete'
    aliases = ('remove',)
    description = 'delete an object'
    args_check = 2
    valid_options = [ ('*', str) ]

    helptext = """\
        == Usage ==
    
        delete <type> <id> [object identifiers]

        == Description ==

        Delete an object. The following arguments are required:

          * type        The type of object to delete
          * id          The object identifier

        Objects can be identified by their name and by their unique id.

        == Available Types ==

        The <type> parameter must be one of the following.

          $types

        == Object Identifiers ==

        Some objects can only exist inside other objects. For example, a disk
        can only exist in the content of a virtual machine. In this case, one
        or more object identifier opties needs to be provided to identify the
        containing object.

        An object identifier is an option of the form '--<type>id <id>'. This
        would identify an object with type <type> and id <id>. See the
        examples section below for a few examples.

        == Examples ==

        Delete a virtual machine named "myvm"

          $ delete vm myvm

        Delete the disk "disk0" from the virtual machine named "myvm"

          $ delete disk disk0 --vmid myvm

        == Return values ==

        This command will exit with one of the following statuses. To see the
        exit status of the last command, type 'status'.

          $statuses
        """

    def execute(self):
        """Execute "delete"."""
        args = self.arguments
        opts = self.options

        if not (TypeHelper.isKnownType(args[0])):
            self.error('no such type: %s' % args[0])

        resource = self.get_object(args[0], args[1], self.resolve_base(opts))
        if resource is None:
            self.error('object does not exist: %s/%s' % (args[0], args[1]))
        elif hasattr(resource, 'delete'):
            result = resource.delete()
        else:
            self.error('object : %s/%s is immutable' % (args[0], args[1]))

        self.context.formatter.format(self.context, result)

    def show_help(self):
        """Show help for "delete"."""
        self.check_connection()
        helptext = self.helptext
        subst = {}
        types = self.get_singular_types()
        subst['types'] = self.format_list(types)
        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses)
        helptext = self.format_help(helptext, subst)
        stdout = self.context.terminal.stdout
        stdout.write(helptext)
