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
from mailmanclient import Client


class Lists():

    """Mailing list related actions."""

    def connect(self, host, port, username, password):
        self.client = Client('%s:%s/3.0' % (host, port), username, password)

        # Tests if connection OK else raise exception
        self.lists = self.client.lists

    def create(self, args):
        """Create a mailing list with specified list_name
           in the domain specified by domain_name.

           :param args: Commandline arguments
        """
        name = args['list'].split('@')
        list_name = name[0]
        domain_name = name[1]

        if domain_name is None or list_name is None:
            print 'Specify domain name and list name'
            exit(1)
        try:
            domain = self.client.get_domain(domain_name)
        except HTTPError:
            print 'Domain not found'
            exit(1)
        try:
            domain.create_list(list_name)
        except HTTPError:
            print 'Mailing list already exists'

    def get_listing(self, domain, detailed, hide_header):
        """Returns list of mailing lists, formatted for tabulation.

            :param domain: Domain name
            :param detailed: Return list details or not
            :param hide_header: Remove header
        """
        table = []
        if detailed:
            if hide_header:
                headers = []
            else:
                headers = ['ID', 'Name', 'Mail host', 'Display Name', 'FQDN']
            table.append(headers)
            if domain is not None:
                try:
                    d = self.client.get_domain(domain)
                except HTTPError:
                    print 'Domain not found'
                    exit(1)
                for i in d.lists:
                    row = []
                    row.append(i.list_id)
                    row.append(i.list_name)
                    row.append(i.mail_host)
                    row.append(i.display_name)
                    row.append(i.fqdn_listname)
                    table.append(row)
            else:
                for i in self.lists:
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
                    print 'Domain not found'
                    exit(1)
                for i in d.lists:
                    table.append([i.list_name])
            else:
                for i in self.lists:
                    table.append([i.list_name])
        return table

    def show(self, args):
        """List the mailing lists in the system or under a domain.

           :param args: Commandline arguments
        """
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

    def list_members(self, list_name):
        pass

    def delete(self, list_name):
        pass
