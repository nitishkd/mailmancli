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
from lib.cmd_processors import preprocess_args, compile_args, validate_args

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
    scopes = ['list', 'user', 'domain']

    def parseline(self, arguments):
        args = preprocess_args(arguments, self.env_on, self.env)
        if not args:
            return ([], [], '')
        try:
            args = compile_args(args, self.env_on, self.env)
        except IndexError:
            pass
        return (args[0], args[1:], ' '.join(args))

    def initialize(self):
        self.mmclient = utils.connect()
        self.scope_classes['list'] = Lists
        self.scope_classes['domain'] = Domains
        self.scope_classes['user'] = Users
        self.scope_classes['preference'] = Preferences

    def refresh_lists(self):
        self.scope_listing['list'] = self.mmclient.lists
        self.scope_listing['domain'] = self.mmclient.domains
        self.scope_listing['user'] = self.mmclient.users

    def do_EOF(self, args):
        print
        print 'Bye!'
        exit(0)

    def do_set(self, args):
        self.env[args[0]] = args[1]
        utils.warn('`%s` set to value `%s`' % (args[0], args[1]))

    def complete_set(self, text, line, begidx, endidx):
        if not text:
            completions = self.env.keys()
        else:
            completions = [k
                           for k in self.env.keys()
                           if k.startswith(text)
                           ]
        return completions

    def do_unset(self, args):
        if args[0] in self.env:
            del self.env[args[0]]
            utils.warn('Shell Variable %s Deleted' % args[0])
        else:
            utils.error('Invalid Argument %s' % args[0])

    def complete_unset(self, text, line, begidx, endidx):
        if not text:
            completions = self.env.keys()
        else:
            completions = [k
                           for k in self.env.keys()
                           if k.startswith(text)
                           ]
        return completions

    def do_show_var(self, args):
        if args[0] in self.env:
            utils.emphasize('Value of %s : %s' % (args[0], self.env[args[0]]))
        else:
            utils.error('Invalid Argument %s' % args[0])

    def complete_show_var(self, text, line, begidx, endidx):
        if not text:
            completions = self.env.keys()
        else:
            completions = [k
                           for k in self.env.keys()
                           if k.startswith(text)
                           ]
        return completions

    def do_disable(self, args):
        if args[0] == 'env':
            self.env_on = False
            utils.emphasize('Environment variables disabled')
        else:
            utils.error('Invalid Argument %s' % args[0])

    def complete_disable(self, text, line, begidx, endidx):
        disable_list = ['env']
        if not text:
            completions = disable_list
        else:
            completions = [k
                           for k in disable_list
                           if k.startswith(text)
                           ]
        return completions

    def do_enable(self, args):
        if args[0] == 'env':
            self.env_on = True
            utils.emphasize('Environment variables enabled')
        else:
            utils.error('Invalid Argument %s' % args[0])

    def complete_enable(self, text, line, begidx, endidx):
        enable_list = ['env']
        if not text:
            completions = enable_list
        else:
            completions = [k
                           for k in enable_list
                           if k.startswith(text)
                           ]
        return completions

    def do_show(self, args):
        if len(args) < 2:
            utils.error('Invalid number of arguments')
            return False
        args.reverse()
        scope = args.pop()
        if args:
            # Pop out `where`
            if args.pop() != 'where':
                utils.error('Invalid syntax. Expected `where` clause')
                return False
        if scope[-1] == 's':
            # Manage Plurality
            scope = scope[:-1]
        filtered_list = self.scope_listing[scope]
        while args:
            try:
                key = args.pop()
                op = args.pop()
                value = args.pop()
                self.data_filter = Filter(key, value, op, filtered_list)
                filtered_list = self.data_filter.get_results()
                if not filtered_list:
                    return False
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

    def complete_show(self, text, line, begidx, endidx):
        if not text:
            completions = self.scopes
        else:
            completions = [k
                           for k in self.scopes
                           if k.startswith(text)
                           ]
        return completions

    def do_create(self, args):
        if len(args) < 2:
            utils.error('Invalid number of arguments')
            return False
        args.reverse()
        scope = args.pop()
        if args:
            if args.pop() != 'where':
                utils.error('Invalid syntax. Expected `where` clause')
                return False
        if scope[-1] == 's':
            scope = scope[:-1]
        properties = {}
        while args:
            try:
                key = args.pop()
                op = args.pop()
                value = args.pop()
                properties[key] = value
                args.pop()
                del op
            except:
                pass
        scope_object = None
        try:
            scope_object = self.scope_classes[scope](self.mmclient)
        except:
            utils.error('Invalid Scope')
            return False
        cmd_arguments = {}
        req_args = []
        try:
            if scope == 'list':
                req_args = ['fqdn_listname']
                cmd_arguments['list'] = properties['fqdn_listname']
            elif scope == 'domain':
                req_args = ['domain', 'contact']
                cmd_arguments['domain'] = properties['domain']
                cmd_arguments['contact'] = properties['contact']
            elif scope == 'user':
                req_args = ['email', 'password', 'name']
                cmd_arguments['email'] = properties['email']
                cmd_arguments['password'] = properties['password']
                cmd_arguments['name'] = properties['name']
        except KeyError:
            utils.error('Invalid number of arguments')
            utils.warn('Required arguments:')
            for i in req_args:
                utils.warn('\t' + i)
            return False
        try:
            scope_object.create(cmd_arguments)
            self.refresh_lists()
        except Exception as e:
            utils.error(e)

    def complete_create(self, text, line, begidx, endidx):
        if not text:
            completions = self.scopes
        else:
            completions = [k
                           for k in self.scopes
                           if k.startswith(text)
                           ]
        return completions

    def do_delete(self, args):
        args.reverse()
        scope = args.pop()
        if args:
            if args.pop() != 'where':
                utils.error('Invalid syntax. Expected `where` clause')
                return False
        if scope[-1] == 's':
            scope = scope[:-1]
        filtered_list = self.scope_listing[scope]
        while args:
            try:
                key = args.pop()
                op = args.pop()
                value = args.pop()
                self.data_filter = Filter(key, value, op, filtered_list)
                filtered_list = self.data_filter.get_results()
                if not filtered_list:
                    return False
                args.pop()
            except:
                pass
        for i in filtered_list:
            if scope == 'list':
                utils.warn('Deleted ' + i.fqdn_listname)
                i.delete()
            elif scope == 'domain':
                utils.warn('Deleted ' + i.base_url)
                self.mmclient.delete_domain(i.mail_host)
            elif scope == 'user':
                utils.warn('Deleted ' + i.display_name)
                i.delete()
            self.refresh_lists()

    def complete_delete(self, text, line, begidx, endidx):
        if not text:
            completions = self.scopes
        else:
            completions = [k
                           for k in self.scopes
                           if k.startswith(text)
                           ]
        return completions

    def do_subscribe(self, args):
        if len(args) < 2:
            utils.error('Invalid number of arguments')
            return False
        if 'to' not in args:
            utils.error('Invalid syntax. Expected to clause')
            return False
        args.reverse()
        scope = args.pop()
        if scope[-1] == 's':
            # Manage Plurality
            scope = scope[:-1]
        users = []
        list_name = None
        user = args.pop()
        while args and user != 'to':
            users.append(user)
            user = args.pop()
        try:
            list_name = args.pop()
        except:
            utils.error('Specify list name')
            return False
        user_object = self.scope_classes['user'](self.mmclient)
        cmd_arguments = {}
        cmd_arguments['users'] = users
        cmd_arguments['list_name'] = list_name
        cmd_arguments['quiet'] = False
        user_object.subscribe(cmd_arguments)

    def do_unsubscribe(self, args):
        if len(args) < 2:
            utils.error('Invalid number of arguments')
            return False
        if 'from' not in args:
            utils.error('Invalid syntax. Expected from clause')
            return False
        args.reverse()
        scope = args.pop()
        if scope[-1] == 's':
            # Manage Plurality
            scope = scope[:-1]
        users = []
        list_name = None
        user = args.pop()
        while args and user != 'from':
            users.append(user)
            user = args.pop()
        try:
            list_name = args.pop()
        except:
            utils.error('Specify list name')
            return False
        user_object = self.scope_classes['user'](self.mmclient)
        cmd_arguments = {}
        cmd_arguments['users'] = users
        cmd_arguments['list_name'] = list_name
        cmd_arguments['quiet'] = False
        user_object.unsubscribe(cmd_arguments)
