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
        parser.add_argument('instance', help='Specify instance',
                            choices=['list', 'domain', 'user'])
        parser.add_argument('action', help='Specify an action',
                            choices=['create', 'delete', 'list'])
        parser.add_argument('-l', '--listname', help='Name of the list')
        parser.add_argument('-d', '--domainname', help='Name of the domain')
        parser.add_argument('-c', '--contact',
                            help='Contact address for domain')
        parser.add_argument('-u', '--username', help='Name of the user')
        parser.add_argument('--ll', help='Long list', action='store_true')

        parser.add_argument('--host', help='REST API host address',
                            default='http://127.0.0.1')
        parser.add_argument('--port', help='REST API host port',
                            default='8001')
        parser.add_argument('--restuser', help='REST API username',
                            default='restadmin')
        parser.add_argument('--restpass', help='REST API password',
                            default='restpass')

    def operate_list(self):
        l = Lists()
        try:
            l.connect(host=self.arguments['host'], port=self.arguments['port'],
                      username=self.arguments['restuser'],
                      password=self.arguments['restpass'])
        except MailmanConnectionError:
            print 'Connection to REST API failed'
            exit(1)
        action = self.arguments['action']
        if action == 'create':
            l.create(self.arguments['domainname'],
                     self.arguments['listname'])
        elif action == 'list':
            l.list(self.arguments['domainname'], self.arguments['ll'])

    def operate_domain(self):
        d = Domains()
        try:
            d.connect(host=self.arguments['host'], port=self.arguments['port'],
                      username=self.arguments['restuser'],
                      password=self.arguments['restpass'])
        except MailmanConnectionError:
            print 'Connection to REST API failed'
            exit(1)
        action = self.arguments['action']
        if action == 'create':
            d.create(self.arguments['domainname'],
                     self.arguments['contact'])

    def run(self):
        method_name = 'operate_' + self.arguments['instance']
        method = getattr(self, method_name)
        method()
