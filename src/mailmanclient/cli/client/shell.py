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

from cmd import Cmd
from mailmanclient.cli.core.lists import Lists
from mailmanclient.cli.core.domains import Domains
from mailmanclient.cli.core.users import Users
from mailmanclient.cli.core.preferences import Preferences
from mailmanclient.cli.lib.mailman_utils import MailmanUtils
from mailmanclient.cli.lib.utils import Filter

utils = MailmanUtils()


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
        """ This method overides the Cmd.onecmd method, but eventully
            calls the Cmd.onecmd function. The purpose of this function
            is to catch the errors at a single point, rather than all
            over the code.
        """
        try:
            return Cmd.onecmd(self, s)
        except Exception as e:
            utils.error(e)
            command = s.split()[0]
            self.do_help(command)
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
            self.scope_classes['list'] = Lists
            self.scope_classes['domain'] = Domains
            self.scope_classes['user'] = Users
            self.scope_classes['preference'] = Preferences
            self.refresh_lists()
        except Exception as e:
            utils.error(e)
            exit(1)

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

    def do_set(self, args):
        """Sets a variable in the environment
 Usage:
  set `<variable>` = `<value>`
        """
        from mailmanclient.cli.client.parsers._set import Set
        parser = Set()
        arguments = parser.parse(self)
        key = arguments['key']
        value = utils.add_shell_vars(arguments['value'], self)
        self.env[key] = value
        utils.warn('`%s` set to value `%s`' % (key, value))

    def do_unset(self, args):
        """Delete a shell environment variable
 Usage:
  unset `<var_name>`"""
        from mailmanclient.cli.client.parsers.unset import Unset
        parser = Unset()
        arguments = parser.parse(self)
        key = arguments['key']
        if key in self.env:
            del self.env[key]
            utils.warn('Shell Variable `%s` Deleted' % key)
        else:
            raise Exception('Invalid Argument `%s`' % key)

    def do_show_var(self, args):
        """Show a shell environment variable
 Usage:
  show_var `<var_name>`"""
        from mailmanclient.cli.client.parsers.show_var import ShowVar
        parser = ShowVar()
        arguments = parser.parse(self)
        key = arguments['key']
        if key in self.env:
            utils.emphasize('Value of %s : %s' % (key, self.env[key]))
        else:
            raise Exception('Invalid Argument %s' % key)

    def do_disable(self, args):
        """Disable the shell environment
 Usage:
  disable env"""
        from mailmanclient.cli.client.parsers.disable import Disable
        parser = Disable()
        parser.parse(self)
        self.env_on = False
        utils.emphasize('Environment variables disabled')

    def do_enable(self, args):
        """Enable the shell environment
 Usage:
  enable env"""
        from mailmanclient.cli.client.parsers.enable import Enable
        parser = Enable()
        parser.parse(self)
        self.env_on = True
        utils.emphasize('Environment variables enabled')

    def do_show(self, args):
        """Show requested mailman objects as a table
 Usage:
  show {domain|user|list} where `<object_attribute>` = `<value>`
  show {domain|user|list} where `<object_attribute>` like `<regex>`
  show {domain|user|list} where `<regex>` in `<list_attribute>`
  show {domain|user|list} where <filter2> and <filter2> ..."""
        from mailmanclient.cli.client.parsers.show import Show
        parser = Show()
        arguments = parser.parse(self)
        scope = arguments['scope']
        filtered_list = self.scope_listing[scope]
        if 'filters' in arguments:
            for i in arguments['filters']:
                key, op, value = i
                value = utils.add_shell_vars(value, self)
                data_filter = Filter()
                filtered_list = data_filter.get_results(key, value, op, filtered_list)
                if not filtered_list:
                    return False
        scope_object = self.scope_classes[scope](self.mmclient)
        cmd_arguments = {}
        if scope == 'list':
            cmd_arguments['list'] = None
            cmd_arguments['csv'] = None
            cmd_arguments['domain'] = None
            cmd_arguments['verbose'] = True
            cmd_arguments['no_header'] = False
        elif scope == 'domain':
            cmd_arguments['domain'] = None
            cmd_arguments['csv'] = None
            cmd_arguments['verbose'] = True
            cmd_arguments['no_header'] = False
        elif scope == 'user':
            cmd_arguments['user'] = None
            cmd_arguments['csv'] = None
            cmd_arguments['list_name'] = None
            cmd_arguments['verbose'] = True
            cmd_arguments['no_header'] = False
        scope_object.show(cmd_arguments, filtered_list)

    def do_create(self, args):
        """Creates mailman Objects
 Usage:
  create user with `email`=`EMAIL` and `password`=`PASSWD` and `name`=`NAME`
  create domain with `name`=`DOMAIN` and `contact`=`CONTACT`
  create list with `fqdn_listname`=`LIST`"""
        from mailmanclient.cli.client.parsers.create import Create
        parser = Create()
        arguments = parser.parse(self)
        scope = arguments['scope']
        properties = arguments['properties']
        scope_object = self.scope_classes[scope](self.mmclient)
        cmd_arguments = {}
        req_args = []
        try:
            if scope == 'list':
                req_args = ['fqdn_listname']
                cmd_arguments['list'] = utils.add_shell_vars(properties['fqdn_listname'], self)
            elif scope == 'domain':
                req_args = ['name', 'contact']
                cmd_arguments['domain'] = utils.add_shell_vars(properties['name'], self)
                cmd_arguments['contact'] = utils.add_shell_vars(properties['contact'], self)
            elif scope == 'user':
                req_args = ['email', 'password', 'name']
                cmd_arguments['email'] = utils.add_shell_vars(properties['email'], self)
                cmd_arguments['password'] = utils.add_shell_vars(properties['password'], self)
                cmd_arguments['name'] = utils.add_shell_vars(properties['name'], self)
        except KeyError:
            utils.error('Invalid arguments')
            utils.warn('The required arguments are:')
            for i in req_args:
                utils.warn('\t' + i)
            return False
        scope_object.create(cmd_arguments)
        self.refresh_lists()

    def do_delete(self, args):
        """Delete specified mailman objects
 Usage:
  delete {domain|user|list} where `<object_attribute>` = `<value>`
  delete {domain|user|list} where `<object_attribute>` like `<regex>`
  delete {domain|user|list} where `<key>` in `<list_attribute>`
  delete {domain|user|list} where <filter1> and <filter2> ..."""
        from mailmanclient.cli.client.parsers.delete import Delete
        parser = Delete()
        arguments = parser.parse(self)
        scope = arguments['scope']
        filtered_list = self.scope_listing[scope]
        if 'filters' in arguments:
            for i in arguments['filters']:
                key, op, value = i
                value = utils.add_shell_vars(value, self)
                data_filter = Filter()
                filtered_list = data_filter.get_results(key, value, op, filtered_list)
        if 'filters' in arguments and arguments['filters'] == []:
            utils.confirm('Delete all %ss?[y/n]' % scope)
            ans = raw_input()
            if ans == 'n':
                return False
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

    def do_subscribe(self, args):
        """Subscribes users to a list
 Usage:
  subscribe users `<email1>` `<email2>` ... to `<list fqdn_name>`"""
        from mailmanclient.cli.client.parsers.subscribe import Subscribe
        parser = Subscribe()
        arguments = parser.parse(self)
        users = arguments['users']
        cleaned_list = []
        for i in users:
            cleaned_list.append(utils.add_shell_vars(i, self))
        users = cleaned_list
        list_name = utils.add_shell_vars(arguments['list'], self)
        user_object = self.scope_classes['user'](self.mmclient)
        cmd_arguments = {}
        cmd_arguments['users'] = users
        cmd_arguments['list_name'] = list_name
        cmd_arguments['quiet'] = False
        user_object.subscribe(cmd_arguments)
        self.refresh_lists()

    def do_unsubscribe(self, args):
        """ Unsubscribes users from a list
 Usage:
  unsubscribe users `<email1>` [`<email2>` ...] from `<list fqdn_name>`
        """
        from mailmanclient.cli.client.parsers.unsubscribe import Unsubscribe
        parser = Unsubscribe()
        arguments = parser.parse(self)
        users = arguments['users']
        cleaned_list = []
        for i in users:
            cleaned_list.append(utils.add_shell_vars(i, self))
        users = cleaned_list
        list_name = utils.add_shell_vars(arguments['list'], self)
        user_object = self.scope_classes['user'](self.mmclient)
        cmd_arguments = {}
        cmd_arguments['users'] = users
        cmd_arguments['list_name'] = list_name
        cmd_arguments['quiet'] = False
        user_object.unsubscribe(cmd_arguments)
        self.refresh_lists()

    def do_update(self, args):
        """Command to set preferences
 Usage:
   update preference `<preference_name>` to `<value>` globally

   update preference `<preference_name>` to `<value>` for member with
    `email` = `foo@bar.com`
    and `list` = `list@domain.org`

   update preference `<preference_name>` to `<value>`
    for user with `email` = `foo@bar.com`

   update preference `<preference_name>` to `<value>`
    for address with `email` = `foo@bar.com`"""
        from mailmanclient.cli.client.parsers.update import Update
        parser = Update()
        arguments = parser.parse(self)
        scope = arguments['scope']
        preferences = self.scope_classes['preference'](self.mmclient)
        cmd_arguments = {}
        cmd_arguments['key'] = arguments['key']
        cmd_arguments['value'] = arguments['value']
        if scope == 'globally':
            cmd_arguments['update_scope'] = 'global'
        else:
            cmd_arguments['update_scope'] = scope
        for i in arguments['filters']:
            cmd_arguments[i] = utils.add_shell_vars(arguments['filters'][i], self)
        preferences.update(cmd_arguments)

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
        keys = self.env.keys()
        keys.extend(self.scopes)
        return self._complete(text, keys)

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

    def complete_subscribe(self, text, line, begidx, endidx):
        return self._complete(text, ['user'])

    def complete_unsubscribe(self, text, line, begidx, endidx):
        return self._complete(text, ['user'])

    def complete_disable(self, text, line, begidx, endidx):
        disable_list = ['env']
        return self._complete(text, disable_list)

    def complete_enable(self, text, line, begidx, endidx):
        enable_list = ['env']
        return self._complete(text, enable_list)

    def complete_update(self, text, line, begidx, endidx):
        _list = ['preference']
        return self._complete(text, _list)
