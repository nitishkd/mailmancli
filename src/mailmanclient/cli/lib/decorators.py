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

from lib.utils import Colorizer


def preprocess_args(nargs):
    """ Decorator that splits the argument string to argument list and
        generalises the commands by replcaing the `=` with spaces. The
        decorator also checks if the the action is supplied the necessary
        number of arguments, specified as decorator argument

        :param nargs: Number of arguments the action has

    """
    def _decorator(function):
        def wrapper(obj, arguments):
            arguments = arguments.replace('=', ' = ')
            arguments = arguments.replace('!=', ' != ')
            arguments = arguments.replace('<', ' < ')
            arguments = arguments.replace('>', ' > ')
            if 'where' not in arguments and nargs == '*':
                arguments += ' where '
            arguments = arguments.split()
            if nargs == '*':
                return function(obj, arguments)
            if len(arguments) != nargs:
                colorize = Colorizer()
                colorize.error('Invalid number of arguments')
                return False
            return function(obj, arguments)
        return wrapper
    return _decorator


def compile_args(env_on, environment):
    """ Replaces the environment variables used in the commands with their
        respective values, if available.

        :param env_on: Use environment variables or not
        :type env_on: Boolean
        :param environment: The environment hash table
        :type environment: Dictionary
    """
    def _decorator(function):
        def wrapper(obj, arguments):
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
            return function(obj, processed_args)
        return wrapper
    return _decorator


def clean_args(function):
    def wrapper(obj, arguments):
        try:
            if arguments[0][0] == '$':
                arguments[0] = arguments[0][1:]
            return function(obj, arguments)
        except:
            pass
    return wrapper
