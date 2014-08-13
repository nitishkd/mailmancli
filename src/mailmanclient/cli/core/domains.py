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


utils = Utils()


class DomainException(Exception):
    """ Exception on invalid domain """
    pass


class Domains():
    """Domain related actions."""

    def __init__(self, client):
        self.client = client

    def create(self, args):
        """Create a domain name with specified domain_name.
           Optionally, the contact address can also be specified.

           :param args: Commandline arguments
           :type args: dictionary
        """
        domain_name = args['domain']
        contact_address = args['contact']

        try:
            self.client.create_domain(domain_name,
                                      contact_address=contact_address)
        except HTTPError as e:
            code = e.getcode()
            if code == 400:
                raise DomainException('Domain already exists')
            else:
                raise DomainException('An unknown HTTPError has occured')

    def show(self, args, domains_ext=None):
        """List the domains in the system.

           :param args: Commandline arguments
           :type args: dictionary
        """
        if args['domain'] is not None:
            self.describe(args)
            return

        headers = []
        fields = ['base_url']
        domains = []

        if domains_ext:
            domains = domains_ext
        else:
            domains = self.client.domains

        if not args['no_header'] and args['verbose']:
            headers = ['Base URL', 'Contact address',
                       'Mail host', 'URL host']

        if args['verbose']:
            fields = ['base_url', 'contact_address', 'mail_host', 'url_host']

        table = utils.get_listing(domains, fields)

        if args['csv']:
            utils.write_csv(table, headers, args['csv'])
        else:
            print tabulate(table, headers=headers, tablefmt='plain')

    def describe(self, args):
        try:
            domain = self.client.get_domain(args['domain'])
        except HTTPError as e:
            code = e.getcode()
            if code == 404:
                raise DomainException('Domain not found')
            else:
                raise DomainException('An unknown HTTPError has occured')
        table = []
        table.append(['Base URL', domain.base_url])
        table.append(['Contact Address', domain.contact_address])
        table.append(['Mail Host', domain.mail_host])
        table.append(['URL Host', domain.url_host])
        utils.set_table_section_heading(table, 'Description')
        table.append([domain.description, ''])
        utils.set_table_section_heading(table, 'Lists')
        for _list in domain.lists:
            table.append([_list.list_id, ''])
        print tabulate(table, tablefmt='plain')

    def delete(self, args):
        try:
            domain = self.client.get_domain(args['domain'])
        except HTTPError as e:
            code = e.getcode()
            if code == 404:
                raise DomainException('Domain not found')
            else:
                raise DomainException('An unknown HTTPError has occured')
        if not args['yes']:
            utils.confirm('Domain `%s` has %d lists.Delete?[y/n]'
                          % (args['domain'], len(domain.lists)))
            confirm = raw_input()
            if confirm == 'y':
                args['yes'] = True
            elif confirm == 'n':
                return
            else:
                raise Exception('Invalid answer')
        self.client.delete_domain(args['domain'])
