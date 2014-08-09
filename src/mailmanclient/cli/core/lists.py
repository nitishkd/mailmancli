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
from mailmanclient.cli.core.domains import DomainException


utils = Utils()


class ListException(Exception):
    """ List Exceptions """
    pass


class Lists():

    """Mailing list related actions."""

    def __init__(self, client):
        self. client = client

    def create(self, args):
        """Create a mailing list with specified list_name
           in the domain specified by domain_name.

           :param args: Commandline arguments
           :type args: dictionary
        """
        name = args['list'].split('@')
        try:
            list_name = name[0]
            domain_name = name[1]
        except IndexError:
            raise ListException('Invalid FQDN list name')
        if list_name.strip() == '' or domain_name.strip() == '':
            raise ListException('Invalid FQDN list name')
        try:
            domain = self.client.get_domain(domain_name)
        except HTTPError:
            raise DomainException('Domain not found')
        try:
            domain.create_list(list_name)
        except HTTPError:
            raise ListException('List already exists')

    def show(self, args, lists_ext=None):
        """List the mailing lists in the system or under a domain.

           :param args: Commandline arguments
           :type args: dictionary
        """
        if args['list'] is not None:
            self.describe(args)
            return

        lists = []
        fields = ['list_id']
        headers = []

        if args['domain']:
            domain = self.client.get_domain(args['domain'])
            lists = domain.lists
        elif lists_ext:
            lists = lists_ext
        else:
            lists = self.client.lists

        if args['verbose']:
            fields = ['list_id', 'list_name',
                      'mail_host', 'display_name',
                      'fqdn_listname']

        if not args['no_header'] and args['verbose']:
            headers = ['ID', 'Name', 'Mail host', 'Display Name', 'FQDN']

        table = utils.get_listing(lists, fields)

        if args['csv']:
            utils.write_csv(table, headers, args['csv'])
        else:
            print tabulate(table, headers=headers, tablefmt='plain')

    def describe(self, args):
        try:
            _list = self.client.get_list(args['list'])
        except HTTPError:
            raise ListException('List not found')
        table = []
        table.append(['List ID', _list.list_id])
        table.append(['List name', _list.list_name])
        table.append(['Mail host', _list.mail_host])
        utils.set_table_section_heading(table, 'List Settings')
        for i in _list.settings:
            table.append([i, str(_list.settings[i])])
        utils.set_table_section_heading(table, 'Owners')
        for owner in _list.owners:
            table.append([owner, ''])
        utils.set_table_section_heading(table, 'Moderators')
        for moderator in _list.moderators:
            table.append([moderator, ''])
        utils.set_table_section_heading(table, 'Members')
        for member in _list.members:
            email = member.address.split('/')[-1]
            table.append([email, ''])
        print tabulate(table, tablefmt='plain')

    def add_moderator(self, args):
        try:
            _list = self.client.get_list(args['list'])
        except HTTPError:
            raise ListException('List not found')
        users = args['users']
        quiet = args['quiet']
        for user in users:
            try:
                _list.add_moderator(user)
                if not quiet:
                    utils.warn('Added %s as moderator' % (user))
            except Exception as e:
                if not quiet:
                    utils.error('Failed to add %s : %s ' %
                                (user, e))

    def add_owner(self, args):
        try:
            _list = self.client.get_list(args['list'])
        except HTTPError:
            raise ListException('List not found')
        users = args['users']
        quiet = args['quiet']
        for user in users:
            try:
                _list.add_owner(user)
                if not quiet:
                    utils.warn('Added %s as owner' % (user))
            except Exception as e:
                if not quiet:
                    utils.error('Failed to add %s : %s ' %
                                (user, e))

    def remove_moderator(self, args):
        try:
            _list = self.client.get_list(args['list'])
        except HTTPError:
            raise ListException('List not found')
        users = args['users']
        quiet = args['quiet']
        for user in users:
            try:
                _list.remove_moderator(user)
                if not quiet:
                    utils.warn('Removed %s as moderator' % (user))
            except Exception as e:
                if not quiet:
                    utils.error('Failed to remove %s : %s ' %
                                (user, e))

    def remove_owner(self, args):
        try:
            _list = self.client.get_list(args['list'])
        except HTTPError:
            raise ListException('List not found')
        users = args['users']
        quiet = args['quiet']
        for user in users:
            try:
                _list.remove_owner(user)
                if not quiet:
                    utils.warn('Removed %s as owner' % (user))
            except Exception as e:
                if not quiet:
                    utils.error('Failed to remove %s : %s ' %
                                (user, e))

    def show_members(self, args):
        from core.users import Users
        users = Users(self.client)
        args['list_name'] = args['list']
        args['user'] = None
        users.show(args)

    def delete(self, args):
        try:
            _list = self.client.get_list(args['list'])
        except HTTPError:
            raise ListException('List not found')
        if not args['yes']:
            utils.confirm('List %s has %d members.Delete?[y/n]'
                          % (args['list'], len(_list.members)))
            confirm = raw_input()
            if confirm == 'y':
                args['yes'] = True
            elif confirm == 'n':
                return
            else:
                raise Exception('Invalid Answer')
        _list.delete()
