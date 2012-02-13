'''
Created on Feb 9, 2012

@author: mpastern
'''

class AutoCompletionHelper(object):

    __completions = []
    __last_line = ''

    @staticmethod
    def __map_options(args, common_options=[]):
        mp = {}
        for key in args.keys():
            if args[key] != None:
                vals = []
                for val in args[key].split(','):
                    vals.append(val.strip())

                if common_options:
                    vals.extend(common_options)

                mp[key] = vals
            else:
                if common_options:
                    mp[key] = common_options
                else:
                    mp[key] = []

        return mp

    @staticmethod
    def _get_verb_replecations(container, text):
        times = 0
        for f in container:
            if text and f.startswith(text):
                times += 1
                if times > 2: break
        return times

    @staticmethod
    def complete(line, text, args, common_options=[], all_options=False):
        '''
        Provides  auto-completion capabilities
        
        @param line: entered line
        @param text: appended text to complete
        @param args: dictionary of verbs and their's options
        @param common_options: common options to append for complete suggestions
        '''

        mp = AutoCompletionHelper.__map_options(args, common_options)
        if not all_options:
            spl = line.split(' ')
            if len(spl) >= 2:
                s_text = text.strip()
                if len(spl) == 2 and text != ' ':
                    repl = AutoCompletionHelper._get_verb_replecations(mp.keys(), s_text)
                    i_completions = [ f + ' ' if text in mp.keys() or repl == 1 else f
                                    for f in mp.keys()
                                    if f.startswith(s_text)
                                    ]
                else:
                    obj = spl[1].strip()
                    repl = AutoCompletionHelper._get_verb_replecations(mp[obj], s_text)
                    i_completions = ['--' + f + ('id ' if f not in common_options else ' ')
                                     if text in mp[obj] or repl == 1 or len(mp[obj]) == 1
                                                                     or (len(mp[obj]) == 2 and 'None' in mp[obj]) == 1
                                     else f
                                    for f in mp[obj]
                                    if f != 'None' and f.startswith(s_text)
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

