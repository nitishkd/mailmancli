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
import sys
import unittest
try:
    from core.domains import Domains, DomainException
except:
    sys.path = [os.path.abspath(os.path.dirname(__file__)) +
                '/../../../cli/'] + sys.path
    from core.domains import Domains, DomainException
from lib.mailman_utils import MailmanUtils


class TestCreateDomain(unittest.TestCase):

    domain_names = []
    utils = MailmanUtils()

    def setUp(self):
        self.client = self.utils.connect()
        self.domain = Domains(self.client)
        self.test_domain = self.utils.get_new_domain_name()
        self.domain_names.append(self.test_domain)
        self.client.create_domain(self.test_domain)

    def test_normal_create(self):
        self.new_domain = self.utils.get_new_domain_name()
        self.domain_names.append(self.new_domain)
        args = {}
        args['domain'] = self.new_domain
        args['contact'] = 'a@b.com'
        self.domain.create(args)

    def test_create_existent_domain(self):
        args = {}
        args['domain'] = self.test_domain
        args['contact'] = 'a@b.com'
        self.assertRaises(DomainException, self.domain.create, args)

    def test_no_postmaster(self):
        self.new_domain = self.utils.get_new_domain_name()
        self.domain_names.append(self.new_domain)
        args = {}
        args['domain'] = self.new_domain
        args['contact'] = None
        self.domain.create(args)

    def tearDown(self):
        for domain in self.domain_names:
            try:
                self.client.delete_domain(domain)
            except Exception:
                pass
