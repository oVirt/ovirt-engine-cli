
from cli.command.command import Command


class SaveCommand(Command):

    name = 'save'
    description = 'save configuration variables'
    args_check = 0
    helptext = """\
        == Usage ==

        save

        == Description ==

        Save the current value of all configuration settings.
        """

    def execute(self):
        self.context.settings.write_config_file()
