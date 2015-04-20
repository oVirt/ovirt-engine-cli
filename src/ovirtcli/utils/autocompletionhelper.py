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

class AutoCompletionHelper(object):

    @staticmethod
    def __map_options(args, common_options=[], specific_options={}, specific_arguments={}):
        mp = {}
        for key in args.keys():
            if args[key] != None:
                vals = []
                for val in args[key].split(','):
                    if val:
                        val = val.strip()
                        vals.extend(
                            AutoCompletionHelper._get_parent_id_options(val)
                        )
                if common_options:
                    vals.extend(common_options[:])

                mp[key] = vals

                if specific_options.has_key(key):
                    mp[key].extend(specific_options[key])

                if specific_arguments.has_key(key):
                    mp[key].extend(specific_arguments[key])
            else:
                if common_options:
                    mp[key] = common_options[:]
                else:
                    mp[key] = []

                if specific_options.has_key(key):
                    mp[key].extend(specific_options[key])

                if specific_arguments.has_key(key):
                    mp[key].extend(specific_arguments[key])
        return mp

    @staticmethod
    def _get_parent_id_options(obj):
        """
        Returns the options corresponding to parent identifiers. The
        parameter is the name of the object, and the result is a list
        containing the options that can be used to specify that object as a
        parent. For example, if the object name is 'vm' then the result
        will be a list containing 'parent-vm-identifier' and 'parent-vm-name'.
        """
        if obj == 'None':
            return []
        return ['parent-%s-identifier' % obj, 'parent-%s-name' % obj]

    @staticmethod
    def _get_verb_replecations(container, text):
        times = 0
        for f in container:
            if text and f.startswith(text if not text.startswith('--')
                                                       else text.strip()[2:]):
                times += 1
                if times > 2: break
        return times

    @staticmethod
    def _is_verb_in_dict_values(dct, text):
        for key in dct.keys():
            if AutoCompletionHelper._get_verb_replecations(dct[key], text) > 0:
                return True
        return False

    @staticmethod
    def complete(line, text, args, common_options=[], specific_options={}, specific_arguments={}, all_options=False):
        '''
        Provides  auto-completion capabilities
        
        @param line: entered line
        @param text: appended text to complete
        @param args: dictionary of verbs and their's options
        @param common_options: common options to append for complete suggestions        
        @param specific_options: type specific options to append for complete suggestions
        @param specific_arguments: type specific arguments to append for complete suggestions
        '''

        mp = AutoCompletionHelper.__map_options(args, common_options, specific_options, specific_arguments)
        if not all_options:
            spl = line.split(' ')
            if len(spl) >= 2:
                s_text = text.strip()
                if len(spl) == 2 and text != ' ':
                    repl = AutoCompletionHelper._get_verb_replecations(mp.keys(), s_text)
                    i_completions = [ f + ' ' if text in mp.keys() or repl == 1 else f
                                    for f in mp.keys()
                                    if f.startswith(s_text if not s_text.startswith('--')
                                                       else text.strip()[2:])
                                    ]
                else:
                    obj = spl[1].strip()
                    repl = AutoCompletionHelper._get_verb_replecations(mp[obj], s_text)
                    i_completions = [('--' if (not AutoCompletionHelper._is_verb_in_dict_values(specific_arguments, f)) else '')
                                     + f + ' '
                                     if text in mp[obj] or repl == 1 or len(mp[obj]) == 1
                                                                     or (len(mp[obj]) == 2 and 'None' in mp[obj]) == 1
                                     else f
                                    for f in mp[obj]
                                    if f != 'None' and f.startswith(s_text  if not s_text.startswith('--')
                                                       else text.strip()[2:])
                                    ]

                return i_completions
            else:
                return mp.keys()[:]
        else:
            if not text:
                i_completions = args.keys()[:]
            else:
                s_text = text.strip()
                repl = AutoCompletionHelper._get_verb_replecations(args.keys(), text)
                i_completions = [ '--' + f + ' ' if repl == 1 or text in args.keys() else f
                                for f in args.keys()
                                if f.startswith(s_text if not s_text.startswith('--')
                                                       else text.strip()[2:])
                                ]

        return i_completions
