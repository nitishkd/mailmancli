#!/usr/bin/python

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

from lib.mailman_utils import MailmanUtils

utils = MailmanUtils()


class Preprocessor():
    shell = None
    nargs = None
    processor = None
    command = None
    arguments = None
    line = None

    def process(self, action):
        """ Decorator that is used to preprocess the command that has been
            entered by the user.
        """
        def wrapper(obj, args):
            self.shell = obj
            self.line = obj.line
            if self.initialize():
                self.processor()
            self.terminate()
            return action(obj, self.arguments)
        return wrapper

    def initialize(self):
        """ Performs primary cleaning of the command.
                1. Removes quotes
                2. Appends spaces around operators
                3. Splits the user entered string at whitespaces
                4. Tries to get the preprocessor function, if absent, ignores
        """
        self.line = self.line.replace('=', ' = ')
        self.line = self.line.replace('!=', ' != ')
        self.line = self.line.replace('<', ' < ')
        self.line = self.line.replace('>', ' > ')
        self.line = self.line.replace("'", ' ')
        self.line = self.line.replace('"', ' ')
        self.arguments = self.line.split()
        self.command = self.arguments[0]
        try:
            self.processor = getattr(self, 'preprocess_' + self.command)
            return True
        except:
            return False

    def stem(self, scope):
        """ Manages plurality of the scope variable."""
        if scope[-1] == 's':
            scope = scope[:-1]
        return scope

    def preprocess_subscribe(self):
        if self.arguments[-2] != 'to':
            utils.error('Invalid Syntax, expected `to` clause')
            return False
        self.arguments = self.arguments[1:]
        scope = self.arguments[0]
        scope = self.stem(scope)
        self.arguments[0] = scope
        if scope != 'user':
            raise Exception('Invalid Scope : %s ' % (scope))
            return False

    def preprocess_unsubscribe(self):
        if self.arguments[-2] != 'from':
            utils.error('Invalid Syntax, expected `from` clause')
            return False
        self.arguments = self.arguments[1:]
        scope = self.arguments[0]
        scope = self.stem(scope)
        self.arguments[0] = scope
        if scope != 'user':
            utils.error('Invalid Scope')
            return False

    def preprocess_show(self):
        nargs = len(self.arguments)
        if nargs < 2:
            raise Exception('Invalid number of arguments')
        if 'where' in self.arguments and nargs < 6:
            raise Exception('Invalid syntax: expected filter after `where`')
        scope = self.arguments[1]
        scope = self.stem(scope)
        self.arguments[1] = scope
        if self.shell.env_on:
            if 'where' not in self.arguments:
                self.arguments.append('where')
            else:
                self.arguments.append('and')
            if scope == 'list':
                if 'domain' in self.shell.env:
                    self.arguments.extend(['mail_host', '=',
                                           self.shell.env['domain'],
                                           'and'])

    def preprocess_enable(self):
        nargs = len(self.arguments)
        if nargs != 2:
            raise Exception('Invalid number of arguments')

    def preprocess_set(self):
        if '=' in self.arguments:
            self.arguments.remove('=')
        nargs = len(self.arguments)
        if nargs != 3:
            raise Exception('Invalid number of arguments')

    def terminate(self):
        """ Final processing of commands, resolves the environment variables,
            reverses the arguments array to make popping possible and
            pops away the command.
        """
        processed_args = []
        for i in self.arguments:
            if i[0] == '$' and self.shell.env_on:
                if (i[1:] in self.shell.env):
                    processed_args.append(self.shell.env[i[1:]])
                else:
                    processed_args.append(i)
            else:
                processed_args.append(i)
        self.arguments = processed_args
        self.arguments.reverse()
        self.arguments.pop()
