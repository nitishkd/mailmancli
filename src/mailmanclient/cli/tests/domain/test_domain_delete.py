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
import mock
import unittest
from urllib2 import HTTPError
try:
    from core.domains import Domains, DomainException
except:
    sys.path = [os.path.abspath(os.path.dirname(__file__)) +
                '/../../../cli/'] + sys.path
    from core.domains import Domains, DomainException
from lib.mailman_utils import MailmanUtils


class TestDeleteDomain(unittest.TestCase):

    domain_names = []
    utils = MailmanUtils()

    def setUp(self):
        self.client = self.utils.connect()
        self.domain = Domains(self.client)

    def test_normal_delete(self):
        new_domain = self.utils.get_new_domain_name()
        self.domain_names.append(new_domain)
        self.client.create_domain(new_domain)
        args = {}
        args['domain'] = new_domain
        with mock.patch('__builtin__.raw_input', return_value='y'):
            args['yes'] = True
            self.domain.delete(args)
        self.assertRaises(HTTPError, self.client.get_domain, new_domain)

    def test_delete_cancel(self):
        new_domain = self.utils.get_new_domain_name()
        self.domain_names.append(new_domain)
        self.client.create_domain(new_domain)
        args = {}
        args['domain'] = new_domain
        with mock.patch('__builtin__.raw_input', return_value='n'):
            args['yes'] = False
            self.domain.delete(args)
        self.assertRaises(HTTPError, self.client.create_domain, new_domain)

    def test_delete_invalid_confirm(self):
        new_domain = self.utils.get_new_domain_name()
        self.domain_names.append(new_domain)
        self.client.create_domain(new_domain)
        args = {}
        args['domain'] = new_domain
        args['yes'] = False
        with mock.patch('__builtin__.raw_input', return_value='no'):
            self.assertRaises(Exception, self.domain.delete, args)

    def test_delete_without_confirm(self):
        new_domain = self.utils.get_new_domain_name()
        self.domain_names.append(new_domain)
        self.client.create_domain(new_domain)
        args = {}
        args['domain'] = new_domain
        args['yes'] = True
        self.domain.delete(args)
        self.assertRaises(HTTPError, self.client.get_domain, new_domain)

    def test_delete_invalid_domain(self):
        new_domain = self.utils.get_new_domain_name()
        self.domain_names.append(new_domain)
        args = {}
        args['domain'] = new_domain
        args['yes'] = True
        self.assertRaises(DomainException, self.domain.delete, args)

    def tearDown(self):
        for domain in self.domain_names:
            try:
                self.client.delete_domain(domain)
            except Exception:
                pass
