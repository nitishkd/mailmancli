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

from urllib2 import HTTPError
from mailmanclient import Client


class Domains():

    """Domain related actions."""

    def connect(self, host, port, username, password):
        self.client = Client('%s:%s/3.0' % (host, port), username, password)

        # Tests if connection OK else raise exception
        self.domains = self.client.domains

    def create(self, domain_name, contact_address):
        """Create a domain name with specified domain_name.
           Optionally, the contact address can also be specified.

           :param domain_name: Name of the domain
           :param contact_address: Domain contact address
        """

        if domain_name is None:
            print 'Specify domain name'
            exit(1)
        try:
            if contact_address is None:
                self.client.create_domain(domain_name)
            else:
                self.client.create_domain(domain_name,
                                          contact_address=contact_address)
        except HTTPError:
            print 'Domain already exists'
