'''
Created on Feb 9, 2012

@author: mpastern
'''

class AutoCompletionHelper(object):

    __completions = []
    __last_line = ''

    @staticmethod
    def __map_options(args):
        mp = {}
        for key in args.keys():
            if args[key] != None:
                vals = []
                for val in args[key].split(','):
                    vals.append(val.strip())
                mp[key] = vals
            else:
                mp[key] = []

        return mp

    @staticmethod
    def _get_verb_replecations(container, text):
        times = 0
        for f in container.keys():
            if text and f.startswith(text):
                times += 1
                if times > 2: break
        return times

    @staticmethod
    def complete(line, text, args, custom={}, all_options=False):
        '''
        Provides  auto-completion capabilities
        
        @param line: entered line
        @param text: appended text to complete
        @param args: verb args
        @param custom: custom options to append for complete suggestions (NOT IMPLEMENTED)
        '''

        i_completions = []

        if not all_options:
            mp = AutoCompletionHelper.__map_options(args)
            sp_line = line.strip().split(' ')
            last = sp_line[len(sp_line) - 1] if len(sp_line) == 2 else sp_line[len(sp_line) - 2]
            last_arg = last if not last.startswith('--') else last[2:]
            if len(sp_line) < 2 or line.find(AutoCompletionHelper.__last_line) == -1 : AutoCompletionHelper.__completions = []


            times = AutoCompletionHelper._get_verb_replecations(mp, text)
            if (len(sp_line) >= 2 and times < 2 and last_arg in mp.keys() and line.endswith(' ')):
                if len(sp_line) > 2:
                    i_completions = [ '--' + f + 'id'
                                    for f in mp[last_arg]
                                    if text and f.strip() != 'None' and f.startswith(text)
                                    ]
                else:
                    i_completions = [ '--' + f + 'id ' \
                                     if not f.startswith('--') and (len(mp[last_arg]) == 1
                                                                    or
                                                                   (len(mp[last_arg]) == 2
                                                                    and
                                                                    'None' in mp[last_arg]))
                                     else f + 'id'
                                     for f in mp[last_arg]
                                     if f.strip() != 'None'
                                    ]


                AutoCompletionHelper.__completions = i_completions
                AutoCompletionHelper.__last_line = line
            else:
                if len(AutoCompletionHelper.__completions) == 0:
                    i_completions = [ f + ' '
                                    for f in mp.keys()
                                    if f and f.startswith(text)
                                    ]
                else:
                    i_completions = [ ('--' + f + ' ') if text else (f + ' ')
                                    for f in AutoCompletionHelper.__completions
                                    if f.startswith(text)
                                    ]
        else:
            if not text:
                i_completions = args.keys()[:]
            else:
                repl = AutoCompletionHelper._get_verb_replecations(args, text)
                i_completions = [ '--' + f + ' ' if text in args.keys() or repl == 1 else f
                                for f in args.keys()
                                if f.startswith(text.strip() if not text.strip().startswith('--')
                                                             else text.strip()[2:])
                                ]

        return i_completions
