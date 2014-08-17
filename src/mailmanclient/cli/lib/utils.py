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
#
# This file is part of the Mailman CLI Project, Google Summer Of Code, 2014
#
# Author    :   Rajeev S <rajeevs1992@gmail.com>
# Mentors   :   Stephen J. Turnbull <stephen@xemacs.org>
#               Abhilash Raj <raj.abhilash1@gmail.com>
#               Barry Warsaw <barry@list.org>

import re
import sys
import csv
from hashlib import sha1
from datetime import datetime
from mailmanclient.cli.lib import colors


class Utils():
    """ General utilities to be used across the CLI """

    WARN = colors.CYAN
    ERROR = colors.RED
    CONFIRM = colors.GREEN
    EMPHASIZE = colors.PURPLE

    # Give colored output on the CLI"
    def warn(self, message):
        print self.WARN % message

    def error(self, message):
        sys.stderr.write((self.ERROR + '\n') % message)

    def confirm(self, message):
        print self.CONFIRM % message,

    def emphasize(self, message):
        print self.EMPHASIZE % message

    def return_emphasize(self, message):
        return self.EMPHASIZE % message
    # End Colors!

    def get_random_string(self, length):
        """ Returns short random strings, less than 40 bytes in length.

        :param length: Length of the random string to be returned
        :type length: int
        """
        if length > 40:
            raise Exception('Specify length less than 40')
        return sha1(str(datetime.now())).hexdigest()[:length]

    def set_table_section_heading(self, table, heading):
        table.append(['', ''])
        table.append([heading, ''])
        table.append(['=============', ''])

    def write_csv(self, table, headers, filename):
        if table == []:
            return

        if 'csv' not in filename:
            filename += '.csv'

        f = open(filename, 'wb')
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if headers:
            writer.writerow(headers)
        for row in table:
            writer.writerow(row)
        f.close()

        return

    def stem(self, arguments):
        """ Allows the scope to be in singular or plural

        :param arguments: The sys.argv, passed from mmclient
        :type arguments: list
        """
        scope = arguments[2]
        if scope[-1] == 's':
            scope = scope[:-1]
        arguments[2] = scope
        return arguments

    def get_listing(self, objects, fields):
        """ Tabulates the set of objects by using the values of each of the
            fileds. """
        table = []
        for obj in objects:
            row = []
            for field in fields:
                try:
                    value = getattr(obj, field)
                except:
                    value = 'None'

                _type = type(value).__name__
                if _type == '_Addresses':
                    row.append(str(value[0]))
                else:
                    row.append(str(value))

            table.append(row)
        return table


class Filter():
    """ This class manages the filtering tasks for the show and delete commands
        The class supports three filters, equality, regular expression search
        and list search.
    """

    def get_results(self, *args):
        op = args[2]
        if op == '=':
            return self.equality(*args)
        elif op == 'like':
            return self.like(*args)
        elif op == 'in':
            return self.in_list(*args)
        else:
            raise Exception('Invalid operator: %s ' % (op))

    def equality(self, key, value, op, data_set):
        copy_set = data_set[:]
        for i in data_set:
            try:
                obj_value = getattr(i, key)
                if obj_value != value:
                    copy_set.remove(i)
            except AttributeError:
                raise Exception('Invalid filter : %s' % key)
        return copy_set

    def in_list(self, key, value, op, data_set):
        copy_set = data_set[:]
        flag = False
        for i in data_set:
            try:
                the_list = getattr(i, key)
            except KeyError:
                copy_set.remove(i)
                continue
            except AttributeError:
                raise Exception('Invalid filter : %s' % key)

            if key == 'members':
                for j in the_list:
                    if self.match_pattern(j.email, value):
                        flag = True
                        break
            elif key == 'lists':
                for j in the_list:
                    if (self.match_pattern(j.list_id, value)
                       or self.match_pattern(j.fqdn_listname, value)):
                        flag = True
                        break
            elif key == 'subscriptions':
                value = value.replace('@', '.')
                for j in the_list:
                    if self.match_pattern(j.list_id, value):
                        flag = True
                        break
            else:
                for j in the_list:
                    if self.match_pattern(j, value):
                        flag = True
                        break
            if not flag:
                copy_set.remove(i)
            flag = False
        return copy_set

    def like(self, key, value, op, data_set):
        copy_set = data_set[:]
        for i in data_set:
            obj_value = None
            try:
                obj_value = getattr(i, key)
            except KeyError:
                copy_set.remove(i)
            except AttributeError:
                raise Exception('Invalid filter : %s' % key)
            if not self.match_pattern(obj_value, value):
                copy_set.remove(i)
        return copy_set

    def match_pattern(self, string, value):
        """ Regular expression matcher, returns the match object
            or None
        """
        pattern = None
        try:
            pattern = re.compile(value.lower())
        except:
            raise Exception('Invalid pattern : %s' % value)
        string = str(string).lower()
        return pattern.match(string)
