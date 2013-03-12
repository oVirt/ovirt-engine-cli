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

    <command> [arguments] [options] [redirection] [pipeline]
    ! <command>

    This parser supports quoted strings for arguments and options, and
    multi-line inputs.
    """

    tokens = ('IPADDR', 'UUID', 'WORD', 'STRING', 'NUMBER', 'OPTION', 'LT', 'LTLT', 'GT', 'GTGT',
              'BANG', 'PIPE', 'NEWLINE', 'MARKER', 'HEREDOC', 'SHELL')
    literals = ('=', ';')
    states = [('heredoc1', 'inclusive'), ('heredoc2', 'exclusive'),
              ('shell', 'exclusive')]

    t_WORD = r'[^ \n\t"\'<>|!\\#;]+'
    t_OPTION = r'-(-[a-zA-Z_][a-zA-Z0-9_]*)+'
    t_LT = r'<'
    t_GT = r'>'
    t_GTGT = r'>>'

    t_ignore = ' \t'
    t_ignore_comment = r'\#.*'
    t_ignore_quoted_newline = r'\\\n'
    t_heredoc2_ignore = ' \t'
    t_shell_ignore = ' \t'

    def t_IPADDR(self, t):
        # ip validity check performed on the server side,
        # this pattern only recognizes the IP address form
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        t.value = str(t.value)
        return t

    def t_UUID(self, t):
        r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}'
        t.value = str(t.value)
        return t

    def t_STRING(self, t):
        r'''(?s)("([^"\\]|\\.)*"|'[^']*')'''
        if t.value[0] == '"':
            t.value = t.value[1:-1].replace(r'\\', '\\')
        else:
            t.value = t.value[1:-1]
        t.value = t.value.replace('\\\n', '')
        return t

    def t_NUMBER(self, t):
        r'[-+]?\d+'
        t.value = int(t.value)
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
        """command : name argument_list option_list redirections pipeline heredoc eol
                   | BANG SHELL eol
                   | eol
        """
        if len(p) == 8:
            if p[6]:
                for i in range(len(p[4])):
                    if p[4][i][0] == '<<':
                        p[4][i] = ('<<', p[6])
                        break
            p[0] = (p[1], p[2], p[3], p[4], p[5])
        elif len(p) == 4:
            p[0] = (p[1], p[2])
        elif len(p) == 2:
            p[0] = None

    def p_name(self, p):
        """name : WORD"""
        p[0] = p[1]

    def p_argument_list(self, p):
        """argument_list : empty
                         | argument
                         | argument_list argument
        """
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_argument(self, p):
        """argument : IPADDR
                    | UUID
                    | WORD
                    | STRING
                    | NUMBER
        """
        p[0] = p[1]

    def p_option_list(self, p):
        """option_list : empty
                       | option
                       | option_list option

        """
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_option(self, p):
        """option : OPTION option_value
                  | OPTION '=' option_value
        """
        if len(p) == 3:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], p[3])

    def p_option_value(self, p):
        """option_value : IPADDR
                        | UUID
                        | WORD
                        | STRING
                        | NUMBER
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
