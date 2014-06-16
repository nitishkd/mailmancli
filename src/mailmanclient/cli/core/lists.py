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
from core.domains import DomainException


colorize = Colorizer()


class ListException(Exception):
    """ List Exceptions """
    pass


class Lists():

    """Mailing list related actions."""

    def __init__(self, client):
        self. client = client

        # Tests if connection OK else raise exception
        lists = self.client.lists
        del lists

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

    def get_listing(self, domain, detailed, hide_header):
        """Returns list of mailing lists, formatted for tabulation.

            :param domain: Domain name
            :type domain: string
            :param detailed: Return list details or not
            :type detailed: boolean
            :param hide_header: Remove header
            :type hide_header: boolean
        """
        lists = self.client.lists
        table = []
        if detailed:
            if hide_header:
                headers = []
            else:
                headers = ['ID', 'Name', 'Mail host', 'Display Name', 'FQDN']
            table.append(headers)
            if domain is not None:
                try:
                    domain = self.client.get_domain(domain)
                except HTTPError:
                    raise DomainException('Domain not found')
                for i in domain.lists:
                    row = []
                    row.append(i.list_id)
                    row.append(i.list_name)
                    row.append(i.mail_host)
                    row.append(i.display_name)
                    row.append(i.fqdn_listname)
                    table.append(row)
            else:
                for i in lists:
                    row = []
                    row.append(i.list_id)
                    row.append(i.list_name)
                    row.append(i.mail_host)
                    row.append(i.display_name)
                    row.append(i.fqdn_listname)
                    table.append(row)
        else:
            table.append([])
            if domain is not None:
                try:
                    d = self.client.get_domain(domain)
                except HTTPError:
                    raise DomainException('Domain not found')
                for i in d.lists:
                    table.append([i.list_id])
            else:
                for i in lists:
                    table.append([i.list_id])
        return table

    def show(self, args):
        """List the mailing lists in the system or under a domain.

           :param args: Commandline arguments
           :type args: dictionary
        """
        if args['list'] is not None:
            self.describe(args)
            return
        domain_name = args['domain']
        longlist = args['verbose']
        hide_header = args['no_header']
        table = self.get_listing(domain_name, longlist, hide_header)
        headers = table[0]
        try:
            table = table[1:]
        except IndexError:
            table = []
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
        table.append(['', ''])
        table.append(['List Settings:', ''])
        table.append(['=============', ''])
        for i in _list.settings:
            table.append([i, str(_list.settings[i])])
        table.append(['', ''])
        table.append(['Owners:', ''])
        table.append(['=============', ''])
        for owner in _list.owners:
            table.append([owner, ''])
        table.append(['', ''])
        table.append(['Moderators:', ''])
        table.append(['=============', ''])
        for moderator in _list.moderators:
            table.append([moderator, ''])
        table.append(['', ''])
        table.append(['Members:', ''])
        table.append(['=============', ''])
        for member in _list.members:
            table.append([member.email, ''])
        # print table
        print tabulate(table, tablefmt='plain')

    def list_members(self, list_name):
        pass

    def delete(self, args):
        try:
            _list = self.client.get_list(args['list'])
        except HTTPError:
            raise ListException('List not found')
        if not args['yes']:
            colorize.confirm('List %s has %d members.Delete?[y/n]'
                             % (args['list'], len(_list.members)))
            confirm = raw_input()
            if confirm == 'y':
                args['yes'] = True
            elif confirm == 'n':
                return
            else:
                raise Exception('Invalid Answer')
        _list.delete()
