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


import cmd
import os
import sys

from ovirtcli.options import OvirtCliOptionParser
from ovirtcli.context import OvirtCliExecutionContext
from ovirtcli.object import create

class Shell(cmd.Cmd):
    """ovirt-engine-cli command processor."""
    ############################# INIT #################################
    def __init__(self, context, parser, completekey='tab', stdin=None, stdout=None):
        cmd.Cmd.__init__(self, completekey=completekey, stdin=stdin, stdout=stdout)
        self.context = context
        self.parser = parser
    ############################# MISC #################################
    PRODUCT = 'oVirt'
    prompt = '[%s shell]# ' % PRODUCT
#    intro = """
#    
#    ##########################
#       Welcome to % s shell
#    ##########################
#    
#    """ % PRODUCT

    doc_header = '%s shell commands:' % PRODUCT
    #misc_header = 'misc_header'
    undoc_header = 'Misc commands:'
    last_output = ''
    ########################### SYSTEM #################################
    def cmdloop(self, intro=None):
        try:
            return cmd.Cmd.cmdloop(self, intro)
        except Exception, e:
            sys.stderr.write('error: %s\n' % str(e))
            return self.cmdloop(intro)

    def emptyline(self):
        print self.prompt

    def onecmd(self, s):
        return cmd.Cmd.onecmd(self, s)

    def onecmd_loop(self, s):
        opts, args = self.parser.parse_args()
        if opts.connect or len(args) == 0:
            #self.__do_verbose_connect(self, self.context, self.parser, opts)
            self.cmdloop()
        else:
            self.cmdloop()

    def precmd(self, line):
        return cmd.Cmd.precmd(self, line)

    def parseline(self, line):
        ret = cmd.Cmd.parseline(self, line)
        return ret

    def do_prompt(self, line):
        "Change the interactive prompt"
        self.prompt = line

    def do_EOF(self, line):
        return True
    ############################# SHELL #################################
    def do_shell(self, line):
        "Runs a shell command ('!' can be used instead of 'shell' command)."
        output = os.popen(line).read()
        print output
        self.last_output = output

    def do_echo(self, line):
        "Prints the input, replacing '$out' with the output of the last shell command"
        if self.last_output:
            print line.replace('$out', self.last_output)
        else: print self.prompt
    ############################ CONFIG #################################
    def copy_environment_vars(self, context):
        """Copy environment variables into configuration variables in the
        execution context."""
        for var in ('url', 'username', 'password'):
            envvar = 'oVirt_%s' % var.upper()
            confvar = 'ovirt-shell:%s' % var
            if envvar in os.environ:
                try:
                    context.settings[confvar] = os.environ[envvar]
                except ValueError, e:
                    sys.stderr.write('error: %s\n' % str(e))
                    return False
        return True


    def copy_cmdline_options(self, options, context, parser):
        """Copy command-line options into configuration variables in the
        execution context."""
        for opt in parser.option_list:
            if not opt.dest:
                continue
            value = getattr(options, opt.dest)
            if value is None:
                continue
            if opt.dest in ('debug', 'verbosity'):
                dest = 'cli:%s' % opt.dest
            else:
                dest = 'ovirt-shell:%s' % opt.dest
            try:
                context.settings[dest] = value
            except KeyError:
                pass
            except ValueError, e:
                sys.stderr.write('error: %s\n' % str(e))
                return False
        return True

    ############################## MAIN #################################
def main():
    #TODO: support reading script from the file
    parser = create(OvirtCliOptionParser)
    context = create(OvirtCliExecutionContext)
    shell = Shell(context, parser)

    if len(sys.argv) > 1:
        args = ''
        if len(sys.argv) > 2:
            args = sys.argv[1] + " "
            for item in sys.argv[2:]:
                args += '"' + item + '" '
        else:
            args = ' '.join(sys.argv[1:])
        shell.onecmd_loop(args)
    else:
        shell.cmdloop()
    ########################### __main__ #################################
if __name__ == '__main__':
    main()
    ######################################################################