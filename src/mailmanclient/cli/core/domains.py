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


colorize = Colorizer()


class DomainException(Exception):
    """ Exception on invalid domain """
    pass


class Domains():
    """Domain related actions."""

    def __init__(self, client):
        self.client = client

        # Tests if connection OK else raise exception
        domains = self.client.domains

    def create(self, args):
        """Create a domain name with specified domain_name.
           Optionally, the contact address can also be specified.

           :param args: Commandline arguments
           :type args: dictionary
        """
        domain_name = args['domain']
        contact_address = args['contact']

        try:
            if contact_address is None:
                self.client.create_domain(domain_name)
            else:
                self.client.create_domain(domain_name,
                                          contact_address=contact_address)
        except HTTPError:
            raise DomainException('Domain already exists')

    def get_listing(self, detailed, hide_header):
        """Returns list of domains, formatted for tabulation.

           :param detailed: Return domain details or not
           :type detailed: boolean
           :param hide_header: Hide header
           :type hide_header: boolean
           :rtype: Returns a table as a nested list
        """
        domains = self.client.domains
        table = []
        if detailed:
            if hide_header:
                headers = []
            else:
                headers = ['Base URL', 'Contact address',
                           'Mail host', 'URL host']
            table.append(headers)
            for i in domains:
                row = []
                row.append(i.base_url)
                row.append(i.contact_address)
                row.append(i.mail_host)
                row.append(i.url_host)
                table.append(row)
        else:
            table.append([])
            for i in domains:
                table.append([i.base_url])
        return table

    def show(self, args):
        """List the domains in the system.

           :param args: Commandline arguments
           :type args: dictionary
        """
        longlist = args['verbose']
        hide_header = args['no_header']
        table = self.get_listing(longlist, hide_header)
        headers = table[0]
        try:
            table = table[1:]
        except IndexError:
            table = []
        print tabulate(table, headers=headers, tablefmt='plain')

    def delete(self, args):
        try:
            domain = self.client.get_domain(args['domain'])
        except HTTPError:
            raise DomainException('Domain not found')
        if not args['yes']:
            colorize.confirm('Domain `%s` has %d lists.Delete?[y/n]'
                             % (args['domain'], len(domain.lists)))
            confirm = raw_input()
            if confirm == 'y':
                args['yes'] = True
            elif confirm == 'n':
                return
            else:
                raise Exception('Invalid answer')
        self.client.delete_domain(args['domain'])
