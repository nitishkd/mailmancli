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


def preprocess_args(arguments, env_on, env):
    """ Decorator that splits the argument string to argument list and
        generalises the commands by replcaing the `=` with spaces. The
        decorator also checks if the the action is supplied the necessary
        number of arguments, specified as decorator argument

        :param nargs: Number of arguments the action has

    """
    query_list = ['show']
    arguments = arguments.replace('=', ' = ')
    arguments = arguments.replace('!=', ' != ')
    arguments = arguments.replace('<', ' < ')
    arguments = arguments.replace('>', ' > ')
    if not arguments:
        return False
    if 'where' not in arguments:
        arguments += ' where '
    else:
        arguments += ' and '
    arguments = arguments.split()
    if env_on and (arguments[0] in query_list):
        if 'domain' in env:
            if 'list' in arguments[1]:
                arguments.extend(['mail_host','=', env['domain'], 'and'])
        if 'list' in env:
            arguments.extend(['list', '=', env['list'], 'and'])
        if 'user' in env:
            arguments.extend(['user', '=', env['user'], 'and'])
    if len(arguments) < 1:
        return False
    return arguments

def validate_args(nargs):
    def _decorator(action):
        def wrapper(obj, arguments):
            utils = MailmanUtils()
            length = len(arguments)
            nargs = nargs - 2
            if length < nargs:
                utils.error('Invalid number of arguments')
                return False
            return action(obj, arguments)
        return wrapper
    return _decorator

def compile_args(arguments, env_on, environment):
    try:
        arguments[0]
    except:
        return False
    processed_args = []
    for i in arguments:
        if i[0] == '$' and env_on:
            if (i[1:] in environment):
                processed_args.append(environment[i[1:]])
            else:
                processed_args.append(i)
        else:
            processed_args.append(i)
    return processed_args
