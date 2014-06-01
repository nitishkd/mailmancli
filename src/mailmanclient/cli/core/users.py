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

from tabulate import tabulate
from urllib2 import HTTPError
from lib.utils import Colorizer
from core.lists import ListException

colorize = Colorizer()


class UserException(Exception):
    """ User Exceptions """
    pass


class Users():

    """User related actions."""

    def __init__(self, client):
        self.client = client

        # Tests if connection OK else raise exception
        self.users = self.client.users

    def create(self, args):
        """Create a user with specified email,
           password and display name.

           :param args: Commandline arguments
        """
        email = args['email']
        password = args['password']
        display_name = args['name']

        try:
            self.client.create_user(email=email,
                                    password=password,
                                    display_name=display_name)
        except HTTPError:
            raise UserException('User already exists')

    def get_listing(self, list_name, detailed, hide_header):
        """Returns list of mailing lists, formatted for tabulation.

            :param domain: list name
            :param detailed: Return a detailed list or not
            :param hide_header: Remove header
        """
        table = []
        if detailed:
            if hide_header:
                headers = []
            else:
                headers = ['Display Name', 'Address', 'Created on', 'User ID']
            table.append(headers)
            if list_name is not None:
                try:
                    _list = self.client.get_list(list_name)
                except HTTPError:
                    raise ListException('List not found')
                for member in _list.members:
                    row = []
                    try:
                        row.append(member.user.display_name)
                        row.append(str(member.user.addresses[0]))
                        row.append(member.user.created_on)
                        row.append(str(member.user.user_id))
                        table.append(row)
                    except:
                        pass
            else:
                for user in self.users:
                    row = []
                    try:
                        row.append(user.display_name)
                        row.append(str(user.addresses[0]))
                        row.append(user.created_on)
                        row.append(str(user.user_id))
                        table.append(row)
                    except:
                        pass
        else:
            table.append([])
            if list_name is not None:
                try:
                    _list = self.client.get_list(list_name)
                except HTTPError:
                    raise ListException('List not found')
                for member in _list.members:
                    table.append([str(member.user.addresses[0])])
            else:
                for user in self.users:
                    try:
                        table.append([str(user.addresses[0])])
                    except:
                        pass
        return table

    def show(self, args):
        """List users in the system.

           :param args: Commandline arguments
        """
        longlist = args['verbose']
        hide_header = args['no_header']
        list_name = args['list_name']
        table = self.get_listing(list_name, longlist, hide_header)
        headers = table[0]
        try:
            table = table[1:]
        except IndexError:
            table = []
        print tabulate(table, headers=headers, tablefmt='plain')

    def delete(self, args):
        try:
            user = self.client.get_user(args['user'])
        except HTTPError:
            raise UserException('User not found')
        if not args['yes']:
            colorize.confirm('Delete user %s?[y/n]' % args['user'])
            confirm = raw_input()
            if confirm == 'y':
                args['yes'] = True
            elif confirm == 'n':
                return
            else:
                raise Exception('Invalid answer')
        user.delete()
