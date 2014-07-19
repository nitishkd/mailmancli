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
from lib.cmd_preprocessors import Preprocessor

utils = MailmanUtils()
cmdprocessor = Preprocessor()


class Shell(Cmd):
    intro = 'Mailman Command Line Interface'
    prompt = '>>>'
    env = {}
    env_on = True
    scope_classes = {}
    scope_listing = {}
    mmclient = None
    scopes = ['list', 'user', 'domain']
    line = None

    def parseline(self, line):
        """ This function sets the line attribute with the complete
            command, which is used at the preprocessing stage"""
        self.line = line
        return Cmd.parseline(self, line)

    def onecmd(self, s):
        """ This method overided the Cmd.onecmd method, but eventully
            calls the Cmd.onecmd function. The purpose of this function
            is to catch the errors at a single point, rather that all
            over the code.
        """
        try:
            return Cmd.onecmd(self, s)
        except Exception as e:
            utils.error(e)
            return False

    def emptyline(self):
        """ Action on empty line entry. If not overridden, the shell executes last
            command on encountering an empty line.
        """
        return False

    def initialize(self):
        """ Method to initialize the shell. Two hash tables are initialised, one
            for storing the class signatures of the mailman Objects and the
            other to store the lists of each object.
        """
        try:
            self.mmclient = utils.connect()
        except Exception as e:
            utils.error(e)
        self.scope_classes['list'] = Lists
        self.scope_classes['domain'] = Domains
        self.scope_classes['user'] = Users
        self.scope_classes['preference'] = Preferences
        self.refresh_lists()

    def refresh_lists(self):
        """ Refreshes the Mailman object list hash tables.
            Invoke this method explicitly whenever the list contents might
            get modified.
        """
        self.scope_listing['list'] = self.mmclient.lists
        self.scope_listing['domain'] = self.mmclient.domains
        self.scope_listing['user'] = self.mmclient.users

    def do_EOF(self, args):
        print
        print 'Bye!'
        exit(0)

    @cmdprocessor.process
    def do_set(self, args):
        key = args.pop()
        value = args.pop()
        self.env[key] = value
        utils.warn('`%s` set to value `%s`' % (key, value))

    @cmdprocessor.process
    def do_unset(self, args):
        if args[0] in self.env:
            del self.env[args[0]]
            utils.warn('Shell Variable %s Deleted' % args[0])
        else:
            utils.error('Invalid Argument %s' % args[0])

    @cmdprocessor.process
    def do_show_var(self, args):
        if args[0] in self.env:
            utils.emphasize('Value of %s : %s' % (args[0], self.env[args[0]]))
        else:
            utils.error('Invalid Argument %s' % args[0])

    @cmdprocessor.process
    def do_disable(self, args):
        if args[0] == 'env':
            self.env_on = False
            utils.emphasize('Environment variables disabled')
        else:
            utils.error('Invalid Argument %s' % args[0])

    @cmdprocessor.process
    def do_enable(self, args):
        if args[0] == 'env':
            self.env_on = True
            utils.emphasize('Environment variables enabled')
        else:
            utils.error('Invalid Argument %s' % args[0])

    @cmdprocessor.process
    def do_show(self, args):
        scope = args.pop()
        if args:
            if args.pop() != 'where':
                utils.error('Invalid syntax. Expected `where` clause')
                return False
        filtered_list = self.scope_listing[scope]
        while args:
            try:
                key = args.pop()
                op = args.pop()
                value = args.pop()
                data_filter = Filter(key, value, op, filtered_list)
                filtered_list = data_filter.get_results()
                if not filtered_list:
                    return False
                args.pop()
            except IndexError:
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

    @cmdprocessor.process
    def do_create(self, args):
        scope = args.pop()
        if args:
            if args.pop() != 'where':
                utils.error('Invalid syntax. Expected `where` clause')
                return False
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
        scope_object.create(cmd_arguments)
        self.refresh_lists()

    @cmdprocessor.process
    def do_delete(self, args):
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
                data_filter = Filter(key, value, op, filtered_list)
                filtered_list = data_filter.get_results()
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

    @cmdprocessor.process
    def do_subscribe(self, args):
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

    @cmdprocessor.process
    def do_unsubscribe(self, args):
        users = []
        list_name = None
        user = args.pop()
        while args and user != 'from':
            users.append(user)
            user = args.pop()
        try:
            list_name = args.pop()
        except:
            raise Exception('Specify list name')
            return False
        user_object = self.scope_classes['user'](self.mmclient)
        cmd_arguments = {}
        cmd_arguments['users'] = users
        cmd_arguments['list_name'] = list_name
        cmd_arguments['quiet'] = False
        user_object.unsubscribe(cmd_arguments)

    def _complete(self, text, keys):
        """ Method for computing the auto suggest suggestions
        """
        if not text:
            completions = keys
        else:
            completions = [k
                           for k in keys
                           if k.startswith(text)
                           ]
        return completions

    def complete_set(self, text, line, begidx, endidx):
        return self._complete(text, self.env.keys())

    def complete_unset(self, text, line, begidx, endidx):
        return self._complete(text, self.env.keys())

    def complete_show_var(self, text, line, begidx, endidx):
        return self._complete(text, self.env.keys())

    def complete_delete(self, text, line, begidx, endidx):
        return self._complete(text, self.scopes)

    def complete_create(self, text, line, begidx, endidx):
        return self._complete(text, self.scopes)

    def complete_show(self, text, line, begidx, endidx):
        return self._complete(text, self.scopes)

    def complete_disable(self, text, line, begidx, endidx):
        disable_list = ['env']
        return self._complete(text, disable_list)

    def complete_enable(self, text, line, begidx, endidx):
        enable_list = ['env']
        return self._complete(text, enable_list)
