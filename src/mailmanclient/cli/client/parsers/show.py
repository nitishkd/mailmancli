from client.parsers.base import Parser
import sys
from lib.mailman_utils import MailmanUtils
sys.path.insert(0, "../..")

import ply.yacc as yacc


class Show(Parser):
    tokens = ('SHOW', 'SCOPE', 'STRING', 'WHERE', 'OP', 'AND')
    literals = ['+', '`']
    t_ignore = " \t"

    def t_SHOW(self, t):
        r'show'
        return t

    def t_SCOPE(self, t):
        '(user|domain|list)s?'
        return self.stem(t)

    def t_WHERE(self, t):
        'where'
        return t

    def t_OP(self, t):
        '=|in|like'
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

    def p_statement_scope(self, p):
        '''S : SHOW SCOPE FILTER'''
        self.arguments['scope'] = p[2]

    def p_filter(self, p):
        '''FILTER : WHERE EXP
                  |'''
        pass

    def p_exp_condition(self, p):
        '''EXP : STRING OP STRING CONJ'''
        if 'filters' not in self.arguments:
            self.arguments['filters'] = []
        if p[2] == 'in':
            self.arguments['filters'].append((p[3], p[2], p[1]))
        else:
            self.arguments['filters'].append((p[1], p[2], p[3]))

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
        utils = MailmanUtils()
        self.arguments = utils.add_reserved_vars(self.arguments, shell)
        return self.arguments
