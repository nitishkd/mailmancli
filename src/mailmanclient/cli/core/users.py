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

from tabulate import tabulate
from urllib2 import HTTPError
from mailmanclient.cli.lib.utils import Utils
from mailmanclient.cli.core.lists import ListException

utils = Utils()


class UserException(Exception):
    """ User Exceptions """
    pass


class Users():

    """User related actions."""

    def __init__(self, client):
        self.client = client

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
        except HTTPError as e:
            code = e.getcode()
            if code == 400:
                raise UserException('User already exists')
            else:
                raise UserException('An unknown HTTPError has occured')

    def show(self, args, users_ext=None):
        """List users in the system.


           :param args: Commandline arguments
           :type args: dictionary
        """
        if args['user'] is not None:
            self.describe(args)
            return

        headers = []
        fields = ['addresses']
        users = []

        if args['verbose']:
            fields = ['display_name', 'addresses', 'created_on', 'user_id']

        if not args['no_header'] and args['verbose']:
            headers = ['Display Name', 'Address', 'Created on', 'User ID']

        if args['list_name']:
            users = self.get_users(args['list_name'])
        elif users_ext:
            users = users_ext
        else:
            users = self.client.users

        table = utils.get_listing(users, fields)

        if args['csv']:
            utils.write_csv(table, headers, args['csv'])
        else:
            print tabulate(table, headers=headers, tablefmt='plain')

    def get_users(self, listname):
        users = []
        _list = self.client.get_list(listname)
        for member in _list.members:
            users.append(member.user)
        return users

    def describe(self, args):
        ''' Describes a user object '''
        user = self.get_user(args['user'])
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
            email = subscription.address.split('/')[-1]
            table.append([email+' at '+str(subscription.list_id),
                         str(subscription.role)])
        print tabulate(table, tablefmt='plain')

    def delete(self, args):
        ''' Deletes a User object '''
        user = self.client.get_user(args['user'])
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
        _list = self.client.get_list(list_name)
        for i in emails:
            try:
                _list.subscribe(i)
                if not args['quiet']:
                    utils.warn('%s subscribed to %s' % (i, list_name))
            except Exception as e:
                if not args['quiet']:
                    utils.error('Failed to subscribe %s : %s' % (i, e))

    def unsubscribe(self, args):
        ''' Unsubsribes a user or a list of users from a list '''
        list_name = args['list_name']
        emails = args['users']
        _list = self.client.get_list(list_name)
        for i in emails:
            try:
                _list.unsubscribe(i)
                if not args['quiet']:
                    utils.warn('%s unsubscribed from %s' % (i, list_name))
            except Exception as e:
                if not args['quiet']:
                    utils.error('Failed to unsubscribe %s : %s' % (i, e))

    def get_list(self, listname):
        try:
            return self.client.get_list(listname)
        except HTTPError as e:
            code = e.getcode()
            if code == 404:
                raise ListException('List not found')
            else:
                raise ListException('An unknown HTTPError has occured')

    def get_user(self, username):
        try:
            return self.client.get_user(username)
        except HTTPError as e:
            code = e.getcode()
            if code == 404:
                raise UserException('User not found')
            else:
                raise UserException('An unknown HTTPError has occured')
