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

from argparse import ArgumentParser
from mailmanclient._client import MailmanConnectionError
from core.lists import Lists
from core.domains import Domains


class CmdParser():
    def __init__(self, command):
        parser = ArgumentParser(description='Mailman Command Tools')
        self.initialize_options(parser)
        self.arguments = vars(parser.parse_args())

    def initialize_options(self, parser):
        action = parser.add_subparsers(dest='action')

        # Parser for the action `show`
        action_show = action.add_parser('show')
        scope = action_show.add_subparsers(dest='scope')

        # Show lists
        show_list = scope.add_parser('list')
        show_list.add_argument('-d',
                               '--domain',
                               help='Filter by DOMAIN')
        show_list.add_argument('-v',
                               '--verbose',
                               help='Detailed listing',
                               action='store_true')
        show_list.add_argument('--no-header',
                               help='Omit headings in detailed listing',
                               action='store_true')

        # Show domains
        show_domain = scope.add_parser('domain')
        show_domain.add_argument('-v',
                                 '--verbose',
                                 help='Detailed listing',
                                 action='store_true')
        show_domain.add_argument('--no-header',
                                 help='Omit headings in detailed listing',
                                 action='store_true')

        # Parser for the action `create`
        action_create = action.add_parser('create')
        scope = action_create.add_subparsers(dest='scope')

        # Create list
        create_list = scope.add_parser('list')
        create_list.add_argument('list',
                                 help='List name. e.g., list@domain.org')
        # Create domain
        create_domain = scope.add_parser('domain')
        create_domain.add_argument('domain',
                                   help='Create domain DOMAIN')
        create_domain.add_argument('--contact',
                                   help='Contact address for domain')
        # Global options
        parser.add_argument('--host', help='REST API host address',
                            default='http://127.0.0.1')
        parser.add_argument('--port', help='REST API host port',
                            default='8001')
        parser.add_argument('--restuser', help='REST API username',
                            default='restadmin')
        parser.add_argument('--restpass', help='REST API password',
                            default='restpass')

    def manage_list(self):
        lists = Lists()
        try:
            lists.connect(host=self.arguments['host'],
                          port=self.arguments['port'],
                          username=self.arguments['restuser'],
                          password=self.arguments['restpass'])
        except MailmanConnectionError:
            print 'Connection to REST API failed'
            exit(1)
        action_name = self.arguments['action']
        action = getattr(lists, action_name)
        action(self.arguments)

    def manage_domain(self):
        domains = Domains()
        try:
            domains.connect(host=self.arguments['host'],
                            port=self.arguments['port'],
                            username=self.arguments['restuser'],
                            password=self.arguments['restpass'])
        except MailmanConnectionError:
            print 'Connection to REST API failed'
            exit(1)
        action_name = self.arguments['action']
        action = getattr(domains, action_name)
        action(self.arguments)

    def run(self):
        method_name = 'manage_' + self.arguments['scope']
        method = getattr(self, method_name)
        method()
