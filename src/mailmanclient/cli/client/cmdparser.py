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
from core.lists import Lists
from core.users import Users
from lib.utils import Colorizer
from mailmanclient import Client
from core.domains import Domains
from core.preferences import Preferences
from mailmanclient._client import MailmanConnectionError


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
        show_list.add_argument('list',
                               help='List details about LIST',
                               nargs='?')
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
        show_list.add_argument('--csv',
                               help='Output as CSV, Specify filename')

        # Show domains
        show_domain = scope.add_parser('domain')
        show_domain.add_argument('domain',
                                 help='List details about DOMAIN',
                                 nargs='?')
        show_domain.add_argument('-v',
                                 '--verbose',
                                 help='Detailed listing',
                                 action='store_true')
        show_domain.add_argument('--no-header',
                                 help='Omit headings in detailed listing',
                                 action='store_true')
        show_domain.add_argument('--csv',
                               help='Output as CSV, Specify filename')

        # Show users
        show_user = scope.add_parser('user')
        show_user.add_argument('user',
                               help='List details about USER',
                               nargs='?')
        show_user.add_argument('-v',
                               '--verbose',
                               help='Detailed listing',
                               action='store_true')
        show_user.add_argument('--no-header',
                               help='Omit headings in detailed listing',
                               action='store_true')
        show_user.add_argument('-l',
                               '--list',
                               help='Specify list name',
                               dest='list_name')
        show_user.add_argument('--csv',
                               help='Output as CSV, Specify filename')

        # Show preferences
        preferences = ['receive_list_copy', 'hide_address',
                       'preferred_language', 'acknowledge_posts',
                       'delivery_mode', 'receive_own_postings',
                       'http_etag', 'self_link', 'delivery_status']
        show_preference = scope.add_parser('preference')
        show_scope = show_preference.add_subparsers(dest='show_scope')

        show_scope.add_parser('global')

        user_show = show_scope.add_parser('user')
        user_show.add_argument('--email',
                               help='Email of user whose '
                               'preference is to be shown',
                               required=True)

        address_show = show_scope.add_parser('address')
        address_show.add_argument('--email',
                                  help='Address whose preference'
                                  ' is to be shown',
                                  required=True)

        member_show = show_scope.add_parser('member')
        member_show.add_argument('--email',
                                 help='Address whose preference'
                                 ' is to be shown',
                                 required=True)
        member_show.add_argument('--list',
                                 help='FQDN name of list',
                                 required=True)

        show_preference.add_argument('key',
                                     help='Specify setting name',
                                     choices=preferences)

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
        # Create users
        create_user = scope.add_parser('user')
        create_user.add_argument('email',
                                 help='Create user foo@bar.com')
        create_user.add_argument('--password',
                                 help='User password',
                                 required=True)
        create_user.add_argument('--name',
                                 help='Display name of the user',
                                 required=True)

        # Parser for the action `delete`
        action_delete = action.add_parser('delete')
        scope = action_delete.add_subparsers(dest='scope')

        # Delete list
        delete_list = scope.add_parser('list')
        delete_list.add_argument('list',
                                 help='List name. e.g., list@domain.org')
        delete_list.add_argument('--yes',
                                 help='Force delete',
                                 action='store_true')
        # Delete domain
        delete_domain = scope.add_parser('domain')
        delete_domain.add_argument('domain',
                                   help='Domain name. e.g., domain.org')
        delete_domain.add_argument('--yes',
                                   help='Force delete',
                                   action='store_true')
        # Delete user
        delete_user = scope.add_parser('user')
        delete_user.add_argument('user',
                                 help='User email e.g., foo@bar.com')
        delete_user.add_argument('--yes',
                                 help='Force delete',
                                 action='store_true')
        # Show Members of a list
        action_show_member = action.add_parser('show-members')
        scope = action_show_member.add_subparsers(dest='scope')
        show_member = scope.add_parser('list')
        show_member.add_argument('list',
                                 help='Show members of LIST')
        show_member.add_argument('-v',
                                 '--verbose',
                                 help='Detailed listing',
                                 action='store_true')
        show_member.add_argument('--no-header',
                                 help='Omit headings in detailed listing',
                                 action='store_true')

        # Parser for the action `subscribe`
        action_subscribe = action.add_parser('subscribe')
        scope = action_subscribe.add_subparsers(dest='scope')
        subscribe_user = scope.add_parser('user')
        subscribe_user.add_argument('users',
                                    help='User email list',
                                    nargs='+')
        subscribe_user.add_argument('-l',
                                    '--list',
                                    help='Specify list name',
                                    dest='list_name',
                                    required=True)
        subscribe_user.add_argument('--quiet',
                                    help='Do not display feedback',
                                    action='store_true')

        # Parser for the action `unsubscribe`
        action_subscribe = action.add_parser('unsubscribe')
        scope = action_subscribe.add_subparsers(dest='scope')
        subscribe_user = scope.add_parser('user')
        subscribe_user.add_argument('users',
                                    help='User email list',
                                    nargs='+')
        subscribe_user.add_argument('-l',
                                    '--list',
                                    help='Specify list name',
                                    dest='list_name',
                                    required=True)
        subscribe_user.add_argument('--quiet',
                                    help='Do not display feedback',
                                    action='store_true')
        # Moderation Tools

        # Add Moderator
        action_add_moderator = action.add_parser('add-moderator')
        scope = action_add_moderator.add_subparsers(dest='scope')
        add_moderator = scope.add_parser('list')
        add_moderator.add_argument('list',
                                   help='Specify list name')
        add_moderator.add_argument('-u',
                                   '--user',
                                   help='User email list',
                                   dest='users',
                                   nargs='+',
                                   required=True)
        add_moderator.add_argument('--quiet',
                                   help='Do not display feedback',
                                   action='store_true')
        # Add Owner
        action_add_owner = action.add_parser('add-owner')
        scope = action_add_owner.add_subparsers(dest='scope')
        add_owner = scope.add_parser('list')
        add_owner.add_argument('list',
                               help='Specify list name')
        add_owner.add_argument('-u',
                               '--user',
                               help='User email list',
                               dest='users',
                               nargs='+')
        add_owner.add_argument('--quiet',
                               help='Do not display feedback',
                               action='store_true')
        # Remove Moderator
        action_remove_moderator = action.add_parser('remove-moderator')
        scope = action_remove_moderator.add_subparsers(dest='scope')
        remove_moderator = scope.add_parser('list')
        remove_moderator.add_argument('list',
                                      help='Specify list name')
        remove_moderator.add_argument('-u',
                                      '--user',
                                      dest='users',
                                      help='User email list',
                                      nargs='+')
        remove_moderator.add_argument('--quiet',
                                      help='Do not display feedback',
                                      action='store_true')
        # Remove Owner
        action_remove_owner = action.add_parser('remove-owner')
        scope = action_remove_owner.add_subparsers(dest='scope')
        remove_owner = scope.add_parser('list')
        remove_owner.add_argument('list',
                                  help='Specify list name')
        remove_owner.add_argument('-u',
                                  '--user',
                                  help='User email list',
                                  dest='users',
                                  nargs='+')
        remove_owner.add_argument('--quiet',
                                  help='Do not display feedback',
                                  action='store_true')
        # Edit preferences
        action_update = action.add_parser('update')
        scope = action_update.add_subparsers(dest='scope')
        update_preference = scope.add_parser('preference')
        update_scope = update_preference.add_subparsers(dest='update_scope')

        update_scope.add_parser('global')

        user_update = update_scope.add_parser('user')
        user_update.add_argument('--email',
                                 help='Email of user whose '
                                 'preference is to be changed',
                                 required=True)

        address_update = update_scope.add_parser('address')
        address_update.add_argument('--email',
                                    help='Address whose preference'
                                    ' is to be changed',
                                    required=True)

        member_update = update_scope.add_parser('member')
        member_update.add_argument('--email',
                                   help='Address whose preference'
                                   ' is to be changed',
                                   required=True)
        member_update.add_argument('--list',
                                   help='FQDN name of list',
                                   required=True)

        update_preference.add_argument('key',
                                       help='Specify setting name',
                                       choices=preferences)
        update_preference.add_argument('value',
                                       help='Specify setting value')
        # Global options
        parser.add_argument('--host', help='REST API host address',
                            default='http://127.0.0.1')
        parser.add_argument('--port', help='REST API host port',
                            default='8001')
        parser.add_argument('--restuser', help='REST API username',
                            default='restadmin')
        parser.add_argument('--restpass', help='REST API password',
                            default='restpass')

    def run(self):
        scopes = {}
        scopes['user'] = Users
        scopes['list'] = Lists
        scopes['domain'] = Domains
        scopes['preference'] = Preferences
        self.arguments['action'] = self.arguments['action'].replace('-', '_')
        host = self.arguments['host']
        port = self.arguments['port']
        username = self.arguments['restuser']
        password = self.arguments['restpass']
        client = Client('%s:%s/3.0' % (host, port),
                        username,
                        password)
        try:
            try:
                scope_object = scopes[self.arguments['scope']](client)
            except MailmanConnectionError:
                raise Exception('Connection to REST API failed')
            action_name = self.arguments['action']
            action = getattr(scope_object, action_name)
            action(self.arguments)
        except Exception as e:
            colorize = Colorizer()
            colorize.error(e)
            exit(1)
