
from ovirtcli.command.command import OvirtCommand
from ovirtcli.utils.typehelper import TypeHelper


class ShowCommand(OvirtCommand):

    name = 'show'
    description = 'show one object'
    args_check = 2
    valid_options = [ ('*', str) ]

    helptext = """\
        == Usage ==
    
        show <type> <id> [object identifiers]

        == Description ==

        Retrieve an object and display information about it. The following
        arguments are required:

          * type        The type of object to retrieve
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

        Show information about the virtual machine "myvm"

          $ show vm myvm

        Show information about the first nic of the virtual machine "myvm"

          $ show nic nic1 --vmid myvm

        == Return values ==

        This command will exit with one of the following statuses. To see the
        exit status of the last command, type 'status'.

          $statuses
        """

    def execute(self):
        """Execute "show"."""
        args = self.arguments
        opts = self.options

        if not (TypeHelper.isKnownType(args[0])):
            self.error('no such type: %s' % args[0])

        self.context.formatter.format(self.context, self.get_object(args[0],
                                                                    args[1],
                                                                    base=self.resolve_base(opts)))

    def __get(self, collection, search_pattern):
        connection = self.check_connection()
        if hasattr(connection, collection):
            return getattr(connection, collection).get(name=search_pattern)
        return None

    def show_help(self):
        """Show help for "show"."""
        self.check_connection()
        subst = {}
        types = self.get_singular_types()
        subst['types'] = self.format_list(types)
        statuses = self.get_statuses()
        subst['statuses'] = self.format_list(statuses)
        helptext = self.format_help(self.helptext, subst)
        stdout = self.context.terminal.stdout
        stdout.write(helptext)
