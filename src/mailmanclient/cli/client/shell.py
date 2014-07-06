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

from cmd import Cmd
from core.lists import Lists
from core.domains import Domains
from core.users import Users
from core.preferences import Preferences
from lib.mailman_utils import MailmanUtils
from lib.utils import Filter
from lib.decorators import preprocess_args, compile_args, clean_args

utils = MailmanUtils()


class Shell(Cmd):
    intro = 'Mailman Command Line Interface'
    prompt = '>>>'
    env = {}
    env_on = True
    scope_classes = {}
    scope_listing = {}
    mmclient = None
    data_filter = None

    def initialize(self):
        self.mmclient = utils.connect()
        self.scope_classes['list'] = Lists
        self.scope_classes['domain'] = Domains
        self.scope_classes['user'] = Users
        self.scope_classes['preference'] = Preferences
        self.scope_listing['list'] = self.mmclient.lists
        self.scope_listing['domain'] = self.mmclient.domains
        self.scope_listing['user'] = self.mmclient.users

    def do_EOF(self, args):
        print
        print 'Bye!'
        exit(0)

    @preprocess_args(2)
    @clean_args
    @compile_args(env_on, env)
    def do_set(self, args):
        self.env[args[0]] = args[1]
        utils.warn('`%s` set to value `%s`' % (args[0], args[1]))

    @preprocess_args(1)
    @clean_args
    @compile_args(env_on, env)
    def do_unset(self, args):
        if args[0] in self.env:
            self.env[args[0]] = None
            utils.warn('Shell Variable %s Deleted' % args[0])
        else:
            utils.error('Invalid Argument %s' % args[0])

    @preprocess_args(1)
    @clean_args
    @compile_args(env_on, env)
    def do_show_var(self, args):
        if args[0] in self.env:
            utils.emphasize('Value of %s : %s' % (args[0], self.env[args[0]]))
        else:
            utils.error('Invalid Argument %s' % args[0])

    @preprocess_args('*')
    @clean_args
    @compile_args(env_on, env)
    def do_show(self, args):
        scope = args[0]
        args.reverse()
        args.pop()
        if args:
            args.pop()
        if scope[-1] == 's':
            scope = scope[:-1]

        filtered_list = self.scope_listing[scope]
        while args:
            key = args.pop()
            op = args.pop()
            value = args.pop()
            self.data_filter = Filter(key, value, op, filtered_list)
            filtered_list = self.data_filter.get_results()
            try:
                args.pop()
            except:
                pass
        scope_object = self.scope_classes[scope](self.mmclient)
        cmd_arguments = {}
        if scope == 'list':
            cmd_arguments['list'] = None
            cmd_arguments['domain'] = None
            cmd_arguments['verbose'] = True
            cmd_arguments['no_header'] = False
        elif scope == 'domain':
            cmd_arguments['domain'] = None
            cmd_arguments['verbose'] = True
            cmd_arguments['no_header'] = False
        elif scope == 'user':
            cmd_arguments['user'] = None
            cmd_arguments['list_name'] = None
            cmd_arguments['verbose'] = True
            cmd_arguments['no_header'] = False
        scope_object.show(cmd_arguments, filtered_list)
