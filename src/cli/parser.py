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


from cli.plyparse import PLYParser
from cli.error import ParseError


class Parser(PLYParser):
    """A parser for CLI commands. The general form of a CLI comand is:

    <command> [parameter] [redirection] [pipeline]
    ! <command>

    A parameter can be an argument or an option.

    This parser supports quoted strings for arguments and options, and
    multi-line inputs.
    """

    tokens = ('WORD', 'STRING', 'OPTION', 'LT', 'LTLT', 'GT', 'GTGT',
              'BANG', 'PIPE', 'NEWLINE', 'MARKER', 'HEREDOC', 'SHELL')
    literals = ('=', ';')
    states = [('heredoc1', 'inclusive'), ('heredoc2', 'exclusive'),
              ('shell', 'exclusive')]

    t_LT = r'<'
    t_GT = r'>'
    t_GTGT = r'>>'

    t_ignore = ' \t'
    t_ignore_comment = r'\#.*'
    t_ignore_quoted_newline = r'\\\n'
    t_heredoc2_ignore = ' \t'
    t_shell_ignore = ' \t'

    # Note that the expression for options has to be before the
    # expression for words because the generated parser tries them in
    # order, and the expression for words is a supperset of the
    # expression for options. If the expression for words goes first
    # then options are never matched.

    def t_OPTION(self, t):
        r'-(-[a-zA-Z_][a-zA-Z0-9_]*)+'
        return t

    def t_WORD(self, t):
        r'[^ \n\t"\'<>|!\\#;]+'
        try:
            t.value = int(t.value)
        except ValueError:
            pass
        return t

    def t_STRING(self, t):
        r'''(?s)("([^"\\]|\\.)*"|'[^']*')'''
        if t.value[0] == '"':
            t.value = t.value[1:-1].replace(r'\\', '\\')
            t.value = t.value.replace('\\"', '"')
        else:
            t.value = t.value[1:-1]
        t.value = t.value.replace('\\\n', '')
        return t

    def t_LTLT(self, t):
        r'<<'
        t.lexer.begin('heredoc1')
        self.heredoc = []
        return t

    def t_BANG(self, t):
        r'!'
        t.lexer.begin('shell')
        return t

    def t_PIPE(self, t):
        r'\|'
        t.lexer.begin('shell')
        return t

    def t_NEWLINE(self, t):
        r'\n'
        return t

    def t_heredoc1_MARKER(self, t):
        r'[a-zA-Z0-9_-]+'
        self.marker = t.value
        return t

    def t_heredoc1_NEWLINE(self, t):
        r'\n'
        t.lexer.begin('heredoc2')

    def t_heredoc2_HEREDOC(self, t):
        r'.*\n'
        if t.value[:-1] != self.marker:
            self.heredoc.append(t.value)
            return None  # return the whole heredoc later as one token
        t.lexer.begin('INITIAL')
        t.value = ''.join(self.heredoc)
        t.lexer.lexpos -= 1  # read newline again
        return t

    def t_shell_SHELL(self, t):
        r'.*(?<!\\)\n'
        t.lexer.begin('INITIAL')
        t.value = t.value.replace('\\\n', '')[:-1]
        t.lexer.lexpos -= 1  # read newline again
        return t

    def t_error(self, t):
        if t.value[:1] in '"\'':
            raise EOFError
        raise ParseError

    t_heredoc2_error = t_error
    t_shell_error = t_error

    def p_main(self, p):
        """main : command
                | main command
        """
        if p[1] is None:
            p[0] = []
        elif len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            p[0] = p[1] + [p[2]]

    def p_command(self, p):
        """command : name parameter_list redirections pipeline heredoc eol
                   | BANG SHELL eol
                   | eol
        """
        if len(p) == 7:
            if p[5]:
                for i in range(len(p[3])):
                    if p[3][i][0] == '<<':
                        p[3][i] = ('<<', p[5])
                        break
            p[0] = (p[1], p[2], p[3], p[4])
        elif len(p) == 4:
            p[0] = (p[1], p[2])
        elif len(p) == 2:
            p[0] = None

    def p_name(self, p):
        """name : WORD"""
        p[0] = p[1]

    def p_parameter_list(self, p):
        """parameter_list : empty
                          | parameter_list parameter
        """
        if len(p) == 2:
            p[0] = []
        else:
            p[0] = p[1] + [p[2]]

    def p_parameter(self, p):
        """parameter : argument
                     | option
        """
        p[0] = p[1]

    def p_argument(self, p):
        """argument : WORD
                    | STRING
        """
        p[0] = p[1]

    def p_option(self, p):
        """option : OPTION option_value
                  | OPTION '=' option_value
        """
        if len(p) == 3:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], p[3])

    def p_option_value(self, p):
        """option_value : WORD
                        | STRING
                        | empty
        """
        p[0] = p[1]

    def p_redirections(self, p):
        """redirections : empty
                        | redirection
                        | redirections redirection
        """
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_redirection(self, p):
        """redirection : LT file
                       | LTLT MARKER
                       | GT file
                       | GTGT file
        """
        p[0] = (p[1], p[2])

    def p_pipeline(self, p):
        """pipeline : PIPE SHELL
                    | empty
        """
        if len(p) == 3:
            p[0] = p[2]

    def p_heredoc(self, p):
        """heredoc : HEREDOC
                   | empty
        """
        p[0] = p[1]

    def p_file(self, p):
        """file : WORD
                | STRING
        """
        p[0] = p[1]

    def p_eol(self, p):
        """eol : ';' NEWLINE
               | NEWLINE
               | ';'
        """
        p[0] = None

    def p_empty(self, p):
        """empty : """

    def p_error(self, p):
        if p is None:
            raise EOFError
        raise ParseError, 'syntax error'
