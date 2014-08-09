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


class Enable(Parser):
    tokens = ('ENABLE', 'WHAT')
    literals = ['=', '`']
    t_ignore = " \t"

    def t_ENABLE(self, t):
        r'enable'
        return t

    def t_WHAT(self, t):
        r'env'
        t.value = t.value.replace('`', '')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        return

    def t_error(self, t):
        raise Exception("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def p_statment(self, p):
        '''S : ENABLE WHAT'''
        self.arguments['what'] = p[2]

    def p_error(self, p):
        if p:
            raise Exception("Syntax error at '%s'" % p.value)
        else:
            raise Exception("Syntax error : Incomplete Command")

    def parse(self, shell):
        yacc.parse(shell.line)
        return self.arguments
