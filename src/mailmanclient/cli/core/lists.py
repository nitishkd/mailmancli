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

from mailmanclient import Client


class Lists():

    """Mailing list related actions."""

    def connect(self, host, port, username, password):
        self.client = Client('%s:%s/3.0' % (host, port), username, password)

        # Test if connection OK else raise exception
        lists = self.client.lists

    def create(self, domain_name, list_name):
        """Create a mailing list with specified list_name
           in the domain specified by domain_name.

           :param domain_name: string Name of the domain
           :param list_name: string Name of the list
        """

        if domain_name is None or list_name is None:
            print 'Specify domain name and list name'
            exit(1)
        try:
            domain = self.client.get_domain(domain_name)
        except Exception:
            print 'Domain not found'
            exit(1)
        try:
            domain.create_list(list_name)
        except Exception:
            print 'Mailing list already exists'

    def delete(self, list_name):
        pass

    def list(self, domain_name, list_name):
        pass

    def list_members(self, list_name):
        pass
