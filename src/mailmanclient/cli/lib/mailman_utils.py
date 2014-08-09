#!/usr/bin/python

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

from mailmanclient import Client, MailmanConnectionError
from mailman.config import config
from mailmanclient.cli.lib.utils import Utils


class MailmanUtils(Utils):

    """ Utilities relating to Mailman
        Client or the REST API
    """

    def __init__(self):
        config.load()

    def connect(self, *args, **kwargs):
        """ Connect to Mailman REST API using the arguments specified.
            Missing arguments are decided from the mailman.cfg file
            return a client object.
        """
        host, port, username, password = self.get_credentials_from_config()

        if 'host' in kwargs and kwargs['host']:
            host = kwargs['host']
        if 'port' in kwargs and kwargs['port']:
            port = kwargs['port']
        if 'username' in kwargs and kwargs['username']:
            username = kwargs['username']
        if 'password' in kwargs and kwargs['password']:
            password = kwargs['password']

        client = Client('%s:%s/3.0' % (host, port),
                        username,
                        password)
        try:
            client.system
        except MailmanConnectionError as e:
            self.error(e)
            exit(1)
        return client

    def get_credentials_from_config(self):
        """ Returns the credentials required for logging on to
            the Mailman REST API, that are read from the Mailman
            configuration.
        """
        host = 'http://' + config.schema['webservice']['hostname']
        port = config.schema['webservice']['port']
        username = config.schema['webservice']['admin_user']
        password = config.schema['webservice']['admin_pass']
        return host, port, username, password

    def get_new_domain_name(self):
        """ Generates the name of a non existent domain """
        client = self.connect()
        while True:
            domain_name = self.get_random_string(10) + '.com'
            try:
                client.get_domain(domain_name)
                continue
            except Exception:
                return domain_name

    def add_shell_vars(self, arg, shell):
        """ Replaces the variables used in the command with thier respective
            values if the values are present in the shell environment, else
            use the variable as such.
        """
        if not shell.env_on or not arg:
            return arg
        if arg[0] == '$' and arg[1:] in shell.env:
                arg = shell.env[arg[1:]]
        return arg

    def add_reserved_vars(self, args, shell):
        """ Adds the reserved variables to a filter query. The reserved variables
            are domain, list and user, which are added to respective scopes and
            atrribute names.
        """
        scope = args['scope']
        if 'filters' not in args:
            args['filters'] = []
        if not shell.env_on:
            return args
        filters = args['filters']
        if scope == 'list':
            if 'domain' in shell.env:
                filters.append(('mail_host', '=', shell.env['domain']))
        elif scope == 'user':
            if 'list' in shell.env:
                filters.append((shell.env['list'], 'in', 'subscriptions'))
        args['filters'] = filters
        return args
