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
#
# This file is part of the Mailman CLI Project, Google Summer Of Code, 2014
#
# Author    :   Rajeev S <rajeevs1992@gmail.com>
# Mentors   :   Stephen J. Turnbull <stephen@xemacs.org>
#               Abhilash Raj <raj.abhilash1@gmail.com>
#               Barry Warsaw <barry@list.org>

import ply.yacc as yacc
from mailmanclient.cli.client.parsers.base import Parser


class Update(Parser):
    tokens = ('UPDATE', 'PREFERENCE', 'STRING', 'TO', 'WITH',
              'AND', 'FOR', 'GLOBALLY', 'DOMAIN')
    literals = ['=', '`']
    t_ignore = " \t"

    def t_UPDATE(self, t):
        r'update'
        return t

    def t_PREFERENCE(self, t):
        'preference'
        return t

    def t_WITH(self, t):
        'with'
        return t

    def t_GLOBALLY(self, t):
        'globally'
        return t

    def t_DOMAIN(self, t):
        'user|address|member'
        return t

    def t_FOR(self, t):
        'for'
        return t

    def t_TO(self, t):
        'to'
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

    def p_statement_update(self, p):
        '''S : UPDATE PREFERENCE STRING TO STRING E'''
        self.arguments['key'] = p[3]
        self.arguments['value'] = p[5]

    def p_domain(self, p):
        '''E : GLOBALLY
               | FOR DOMAIN WITH EXP'''
        try:
            self.arguments['scope'] = p[2]
        except IndexError:
            self.arguments['scope'] = p[1]

    def p_exp_condition(self, p):
        '''EXP : STRING "=" STRING CONJ'''
        if 'filters' not in self.arguments:
            self.arguments['filters'] = {}
        self.arguments['filters'][p[1]] = p[3]

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
        if 'filters' not in self.arguments:
            self.arguments['filters'] = {}
        return self.arguments
