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

import re
import sys
from hashlib import sha1
from datetime import datetime


class Colorizer():
    " Give colored output on the CLI"

    def warn(self, message):
        print "\033[93m%s\033[0m" % message

    def error(self, message):
        sys.stderr.write("\033[91m%s\033[0m\n" % message)

    def confirm(self, message):
        print "\033[92m%s\033[0m" % message,

    def emphasize(self, message):
        print "\033[92m%s\033[0m" % message


class Utils(Colorizer):
    """ General utilities to be used across the CLI """

    def get_random_string(self, length):
        """ Returns short random strings, less than 40 bytes in length.

        :param length: Length of the random string to be returned
        :type length: int
        """
        try:
            return sha1(str(datetime.now())).hexdigest()[:length]
        except IndexError:
            raise Exception('Specify length less than 40')

    def set_table_section_heading(self, table, heading):
        table.append(['', ''])
        table.append([heading, ''])
        table.append(['=============', ''])


class Filter():
    key = None
    value = None
    operator = None
    data_set = []
    utils = Utils()

    def __init__(self, key, value, operator, data):
        self.key = key
        self.value = value
        self.operator = operator
        if operator == 'in':
            self.key, self.value = self.value, self.key
        self.data_set = data

    def get_results(self):
        if self.operator == '=':
            return self.equality()
        elif self.operator == 'like':
            return self.like()
        elif self.operator == 'in':
            return self.in_list()

    def equality(self):
        copy_set = self.data_set[:]
        for i in self.data_set:
            try:
                obj_value = getattr(i, self.key)
                if obj_value != self.value:
                    copy_set.remove(i)
            except:
                if self.key not in ['domain', 'user', 'list']:
                    self.utils.error('Invalid filter : %s' % self.key)
                    return False
        return copy_set

    def in_list(self):
        copy_set = self.data_set[:]
        flag = False
        for i in self.data_set:
            try:
                obj_value = getattr(i, self.key)
                if self.key == 'members':
                    for j in obj_value:
                        if self.value == str(j.email):
                            flag = True
                            break
                elif self.key == 'lists':
                    for j in obj_value:
                        if ((self.value == str(j.list_id))
                           or (self.value == str(j.fqdn_listname))):
                            flag = True
                            break
                else:
                    for j in obj_value:
                        if self.value == str(j):
                            flag = True
                            break
                if not flag:
                    copy_set.remove(i)
                flag = False
            except:
                if self.key not in ['domain', 'user', 'list']:
                    self.utils.error('Invalid filter : %s' % self.key)
                    return False
        return copy_set

    def like(self):
        copy_set = self.data_set[:]
        pattern = None
        try:
            pattern = re.compile(self.value.lower())
        except:
            self.utils.error('Invalid pattern : %s' % self.value)
            return False
        for i in self.data_set:
            try:
                obj_value = getattr(i, self.key)
                obj_value = str(obj_value).lower()
                if not pattern.match(obj_value):
                    copy_set.remove(i)
            except:
                if self.key not in ['domain', 'user', 'list']:
                    self.utils.error('Invalid filter : %s' % self.key)
                    return
        return copy_set


def CmdPreprocessor(arguments):
    """ Allows the scope to be in singular or plural
    :param arguments: The sys.argv, passed from mmclient
    :type arguments: list
    """
    scope = arguments[2]
    if scope[-1] == 's':
        scope = scope[:-1]
    arguments[2] = scope
    return arguments
