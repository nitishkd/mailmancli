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


def preprocess_args(arguments):
    """ Decorator that splits the argument string to argument list and
        generalises the commands by replcaing the `=` with spaces. The
        decorator also checks if the the action is supplied the necessary
        number of arguments, specified as decorator argument

        :param nargs: Number of arguments the action has

    """
    arguments = arguments.replace('=', ' = ')
    arguments = arguments.replace('!=', ' != ')
    arguments = arguments.replace('<', ' < ')
    arguments = arguments.replace('>', ' > ')
    arguments = arguments.split()
    return arguments


def clean_args(arguments):
    try:
        if arguments[0][0] == '$':
            arguments[0] = arguments[0][1:]
    except:
        pass
    return arguments


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
