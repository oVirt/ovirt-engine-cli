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


from ovirtcli.shell.cmdshell import CmdShell
from ovirtcli.utils.typehelper import TypeHelper
from ovirtcli.utils.autocompletionhelper import AutoCompletionHelper
from ovirtsdk.infrastructure import brokers
from ovirtcli.utils.methodhelper import MethodHelper


class ActionCmdShell(CmdShell):
    NAME = 'action'

    def __init__(self, context):
        CmdShell.__init__(self, context)
        self.complete_exceptions = ['delete', 'update']
        self.identifier_template = '--%s-identifier'

    def do_action(self, args):
        return self.context.execute_string(ActionCmdShell.NAME + ' ' + args + '\n')

    def __add_resource_specific_options(self, obj, specific_options, line, key=None):
        obj_type = TypeHelper.getDecoratorType(TypeHelper.to_singular(obj))
        gda = MethodHelper.get_documented_arguments
        gat = TypeHelper.get_actionable_types
        memeber = key if key is not None else obj
        method_args = []
        action = None

        if obj_type and hasattr(brokers, obj_type):
            action = self.__get_method_name_by_args(obj,
                                                    line.split(' '),
                                                    gat(expendNestedTypes=True),
                                                    line)
            if action:
                obj_typ_ref = getattr(brokers, obj_type)
                if obj_typ_ref and hasattr(obj_typ_ref, action):
                    method_args = gda(method_ref=getattr(obj_typ_ref, action),
                                      as_params_collection=True,
                                      spilt_or=True)
                    if method_args:
                        specific_options[memeber] = method_args

    def __get_resource_actions(self, obj, args, line):
        gom = MethodHelper.get_object_methods
        gdt = TypeHelper.getDecoratorType
        obj_type = gdt(obj)
        actions = []

        if obj_type:
            #add base resource actions
            actions = gom(getattr(brokers, obj_type),
                          exceptions=self.complete_exceptions)

            #add sub-resources actions
            if  args.has_key(obj) and args[obj]:
                self.__add_sub_resourse_actions(obj, args, line, actions)

        return actions


    def __get_method_name_by_args(self, obj, spl, args, line):
        actions = self.__get_resource_actions(obj, args, line)

        for item in spl:
            if item in actions: return item

    def __add_sub_resourse_actions(self, obj, args, line, actions):
        gdt = TypeHelper.getDecoratorType
        gom = MethodHelper.get_object_methods

        if obj in args.keys():
            for cons in args[obj].split(', '):
                spl = line.strip().split(' ')
                if cons != 'None':
                    spl.append(self.identifier_template % cons)
                    base = self._resolve_base(spl[1:])
                    if base:
                        obj_type = gdt(TypeHelper.to_singular(base))
                        actions.extend(gom(getattr(brokers, obj_type),
                                           exceptions=self.complete_exceptions))


    def __add_resource_specific_arguments(self, obj, specific_options, line, key=None):
        gdt = TypeHelper.getDecoratorType
        obj_type = gdt(TypeHelper.to_singular(obj))
        args = TypeHelper.get_actionable_types(expendNestedTypes=True)
        gom = MethodHelper.get_object_methods
        actions = []

        method = self.__get_method_name_by_args(obj, line.split(' '), args, line)

        # collect resource args if yet not used
        if not method and obj_type and hasattr(brokers, obj_type):
            #add base resource actions
            actions = gom(getattr(brokers, obj_type),
                          exceptions=self.complete_exceptions)

            if args.has_key(obj) and args[obj]:
                #add sub-resources actions
                self.__add_sub_resourse_actions(obj, args, line, actions)

        specific_options[obj if key == None else key] = actions


    def __get_action_args(self, line):
        args = TypeHelper.get_actionable_types(expendNestedTypes=True)
        spl = line.rstrip().split(' ')
        gom = MethodHelper.get_object_methods
        gdt = TypeHelper.getDecoratorType

        if len(spl) >= 3:
            new_cons = ''
            obj = spl[1].strip()

            #top level resource in possibilities
            if args.has_key(obj) and args[obj] and args[obj].find('None') != -1:
                act = spl[3].strip() if len(spl) > 3 \
                                     else spl[-1].strip()
            #possibilities refer only to the sub-resource
            else:
                for item in spl:
                    if item.endswith('-identifier'):
                        args[obj] = new_cons
                        return args
                return args

            for cons in args[obj].split(', '):
                if cons == 'None':
                    obj_type = gdt(obj)
                    if not obj_type: continue
                    actions = gom(getattr(brokers, obj_type),
                                  exceptions=self.complete_exceptions)
                    if actions and act in actions:
                        new_cons += 'None, '
                else:
                    tmp_spl = spl[:]
                    tmp_spl.append(self.identifier_template % cons)
                    base = self._resolve_base(tmp_spl[1:])
                    if base:
                        obj_type = gdt(TypeHelper.to_singular(base))
                        if not obj_type: continue
                        actions = gom(getattr(brokers, obj_type),
                                      exceptions=self.complete_exceptions)
                        if actions and act in actions:
                            new_cons += cons + ', '

            args[obj] = new_cons[:len(new_cons) - 2] if len(new_cons) > 3 \
                                                     else ''

        return args

    def complete_action(self, text, line, begidx, endidx):
        args = self.__get_action_args(line)

        specific_options = self.get_resource_specific_options(args,
                                                              line,
                                                              callback=self.__add_resource_specific_options)

        specific_arguments = self.get_resource_specific_options(args,
                                                                line,
                                                                callback=self.__add_resource_specific_arguments)

        return AutoCompletionHelper.complete(line,
                                             text,
                                             args,
                                             specific_options=specific_options,
                                             specific_arguments=specific_arguments)

    def is_action_argument(self, line, key):
        args = self.__get_action_args(line)
        if key in args:
            return True
        specific_options = self.get_resource_specific_options(args,
                                                              line,
                                                              callback=self.__add_resource_specific_options)
        for arg_key in specific_options.keys():
             if key in specific_options[arg_key]:
                 return True
        return False

