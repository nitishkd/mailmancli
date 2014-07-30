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

from client.parsers.base import Parser
import sys
sys.path.insert(0, "../..")

import ply.yacc as yacc


class Create(Parser):
    tokens = ('CREATE', 'SCOPE', 'STRING', 'WITH', 'AND')
    literals = ['+', '`', '=']
    t_ignore = " \t"

    def t_CREATE(self, t):
        r'create'
        return t

    def t_SCOPE(self, t):
        'user|domain|list'
        return t

    def t_WITH(self, t):
        'with'
        return t

    def t_AND(self, t):
        'and'
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

    def p_start_statement(self, p):
        '''S : CREATE SCOPE WITH EXP'''
        self.arguments['scope'] = p[2]

    def p_exp_condition(self, p):
        '''EXP : STRING "=" STRING CONJ'''
        if 'properties' not in self.arguments:
            self.arguments['properties'] = {}
        self.arguments['properties'][p[1]] = p[3]

    def p_conj_exp(self, p):
        ''' CONJ : AND EXP
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
