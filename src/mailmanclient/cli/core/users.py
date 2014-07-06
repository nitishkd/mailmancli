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
from lib.utils import Utils
from core.lists import ListException

utils = Utils()


class UserException(Exception):
    """ User Exceptions """
    pass


class Users():

    """User related actions."""

    def __init__(self, client):
        self.client = client

        # Tests if connection OK else raise exception
        users = self.client.users
        del users

    def create(self, args):
        """Create a user with specified email,password and display name.

           :param args: Commandline arguments
           :type args: dictionary
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

    def get_listing(self, list_name, detailed, hide_header, users_ext):
        """Returns list of mailing lists, formatted for tabulation.

            :param list_name: Name of the list whose members are to be listed
            :type list_name: string
            :param detailed: Return a detailed list or not
            :type detailed: boolean
            :param hide_header: Remove header of detailed listing
            :type hide_header: boolean
            :rtype: Returns a table in form of nested lists
        """
        users = self.client.users
        table = []
        if detailed:
            if hide_header:
                headers = []
            else:
                headers = ['Display Name', 'Address', 'Created on', 'User ID']
            table.append(headers)
            if users_ext is not None:
                users = users_ext
            if list_name is not None:
                try:
                    user = self.client.get_list(list_name)
                except HTTPError:
                    raise ListException('List not found')
                for member in user.members:
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
                for user in users:
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
                    user = self.client.get_list(list_name)
                except HTTPError:
                    raise ListException('List not found')
                for member in user.members:
                    table.append([str(member.user.addresses[0])])
            else:
                for user in users:
                    try:
                        table.append([str(user.addresses[0])])
                    except:
                        pass
        return table

    def show(self, args, users_ext=None):
        """List users in the system.

           :param args: Commandline arguments
           :type args: dictionary
        """
        if args['user'] is not None:
            self.describe(args)
            return
        longlist = args['verbose']
        hide_header = args['no_header']
        list_name = args['list_name']
        table = self.get_listing(list_name, longlist, hide_header, users_ext)
        headers = table[0]
        try:
            table = table[1:]
        except IndexError:
            table = []
        print tabulate(table, headers=headers, tablefmt='plain')

    def describe(self, args):
        ''' Describes a user object '''
        try:
            user = self.client.get_user(args['user'])
        except HTTPError:
            raise UserException('User not found')
        table = []
        table.append(['User ID', user.user_id])
        table.append(['Display Name', user.display_name])
        table.append(['Created on', user.created_on])
        table.append(['Self Link', user.self_link])
        utils.set_table_section_heading(table, 'User Preferences')
        preferences = user.preferences._preferences
        for i in preferences:
            table.append([i, str(preferences[i])])
        utils.set_table_section_heading(table, 'Subscription List IDs')
        for _list in user.subscription_list_ids:
            table.append([_list, ''])
        utils.set_table_section_heading(table, 'Subscriptions')
        for subscription in user.subscriptions:
            table.append([subscription.email+' at '+str(subscription.list_id),
                         str(subscription.role)])
        print tabulate(table, tablefmt='plain')

    def delete(self, args):
        ''' Deletes a User object '''
        try:
            user = self.client.get_user(args['user'])
        except HTTPError:
            raise UserException('User not found')
        if not args['yes']:
            utils.confirm('Delete user %s?[y/n]' % args['user'])
            confirm = raw_input()
            if confirm == 'y':
                args['yes'] = True
            elif confirm == 'n':
                return
            else:
                raise Exception('Invalid answer')
        user.delete()

    def subscribe(self, args):
        ''' Subsribes a user or a list of users to a list '''
        list_name = args['list_name']
        emails = args['users']
        try:
            user = self.client.get_list(list_name)
        except HTTPError:
            raise ListException('List not found')
        for i in emails:
            try:
                user.subscribe(i)
                if not args['quiet']:
                    utils.warn('%s subscribed to %s' % (i, list_name))
            except Exception as e:
                if not args['quiet']:
                    utils.error('Failed to subscribe %s : %s' % (i, e))

    def unsubscribe(self, args):
        ''' Unsubsribes a user or a list of users from a list '''
        list_name = args['list_name']
        emails = args['users']
        try:
            user = self.client.get_list(list_name)
        except HTTPError:
            raise ListException('List not found')
        for i in emails:
            try:
                user.unsubscribe(i)
                if not args['quiet']:
                    utils.warn('%s unsubscribed from %s' % (i, list_name))
            except Exception as e:
                if not args['quiet']:
                    utils.error('Failed to unsubscribe %s : %s' % (i, e))
