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

import os
from ConfigParser import ConfigParser
from mailmanclient import Client
from lib.utils import Utils


class MailmanUtils(Utils):

    """ Utilities relating to Mailman
        Client or the REST API
    """

    def connect(self):
        """ Connect to Mailman REST API and
            return a client object.
        """
        cfgparser = ConfigParser()
        cfgparser.read(os.path.dirname(__file__) + '/../config.ini')
        host = cfgparser.get('LOGIN', 'host')
        port = cfgparser.get('LOGIN', 'port')
        username = cfgparser.get('LOGIN', 'username')
        password = cfgparser.get('LOGIN', 'password')
        client = Client('%s:%s/3.0' % (host, port),
                        username,
                        password)
        return client

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
