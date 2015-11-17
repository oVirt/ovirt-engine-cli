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

import itertools
import os
import sys

from ovirtcli.infrastructure.settings import OvirtCliSettings
from ovirtcli.utils.optionhelper import OptionHelper
from ovirtcli.utils.typehelper import TypeHelper


class CmdShell(object):
    def __init__(self, context):
        self.__context = context
        self.__owner = self

    def get_owner(self):
        return self.__owner

    def get_context(self):
        return self.__context

    context = property(get_context, None, None, None)
    owner = property(get_owner, None, None, None)

    ############################ CONFIG #################################
    def copy_environment_vars(self, context):
        """Copy environment variables into configuration variables in the
        execution context."""
        for var in ('url', 'username', 'password'):
            envvar = OvirtCliSettings.PRODUCT + '_%s' % var.upper()
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
    #####################################################################
    def __generate_resource_specific_options__(self, args, line, callback):
        specific_options = {}

        if line:
            spl = line.rstrip().split(' ')
            if len(spl) >= 2:
                obj = spl[1].strip()
                base = self._resolve_base(spl[1:])
                if base:
                    callback(base, specific_options, line=line, key=obj)
                else:
                    callback(obj, specific_options, line=line)
            elif len(spl) == 2 and spl[1] != '' and spl[1].strip() in args.keys():
                callback(spl[1].strip(), specific_options, line=line)

            return specific_options

    def _resolve_base(self, args):
        """
        Resolves a base object from a set of '--parent-type-identifier'
        or '--parent-type-name' options.
        """
        parent_candidates = [item for item in args
                if OptionHelper.is_parent_id_option(item)]
        parent_candidates_permutations = list(itertools.permutations(parent_candidates))

        if parent_candidates_permutations[0]:
            for combination in parent_candidates_permutations:
                candidates = [OptionHelper.get_parent_id_type(item)
                        for item in combination
                        if OptionHelper.is_parent_id_option(item)]
                candidate = (''.join(candidates) + args[0]).lower()
                dt = TypeHelper.getDecoratorType(candidate)
                if dt: return dt

        return None

    def get_resource_specific_options(self, args, line, callback):
        """
         Generates resource specific options. 
         
         @param args: args to process 
         @param line: line to process
         @param callback: callback to call when done
         
        """
        return self.__generate_resource_specific_options__(args, line, callback)

    def _error(self, msg):
        """
        prints error to stderr

        @param msg: error message
        """
        sys.stderr.write("\nerror: " + msg + "\n")
        sys.stdout.write("\n")
