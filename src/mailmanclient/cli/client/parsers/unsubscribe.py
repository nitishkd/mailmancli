# Copyright (C) 2010-2014 by the Free Software Foundation, Inc.
#
# This file is part of mailman.client.
#
# mailman.client is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# mailman.client is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mailman.client.  If not, see <http://www.gnu.org/licenses/>.

from mailmanclient.cli.client.parsers.base import Parser
import sys
sys.path.insert(0, "../..")

import ply.yacc as yacc


class Unsubscribe(Parser):
    tokens = ('UNSUBSCRIBE', 'USER', 'STRING', 'FROM')
    literals = ['+', '`', ',']
    t_ignore = " \t"

    def t_UNSUBSCRIBE(self, t):
        r'unsubscribe'
        return t

    def t_USER(self, t):
        '(user)s?'
        return self.stem(t)

    def t_FROM(self, t):
        'from'
        return t

    def t_STRING(self, t):
        r'`([a-zA-Z0-9_@\.\*\-\$ ]*)`'
        t.value = t.value.replace('`', '')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        return

    def t_error(self, t):
        raise Exception("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def p_statement_unsubscribe(self, p):
        '''S : UNSUBSCRIBE USER USERLIST FROM STRING'''
        self.arguments['list'] = p[5]
        self.arguments['scope'] = p[2]

    def p_get_users(self, p):
        '''USERLIST : STRING NEXT'''
        if 'users' not in self.arguments:
            self.arguments['users'] = []
        self.arguments['users'].append(p[1])

    def p_next(self, p):
        '''NEXT : USERLIST
                |'''
        pass

    def p_error(self, p):
        if p:
            raise Exception("Syntax error at '%s'" % p.value)
        else:
            raise Exception("Syntax error : Incomplete Command")

    def parse(self, shell):
        yacc.parse(shell.line)
        return self.arguments
