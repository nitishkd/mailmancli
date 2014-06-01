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
import random
import unittest
from mock import patch
from StringIO import StringIO
try:
    from core.domains import Domains
except:
    sys.path = [os.path.abspath(os.path.dirname(__file__)) +
                '/../../../cli/'] + sys.path
    from core.domains import Domains
from lib.mailman_utils import MailmanUtils


class TestCreateDomain(unittest.TestCase):

    domain_names = []
    utils = MailmanUtils()

    def setUp(self):
        self.client = self.utils.connect()
        self.domain = Domains(self.client)

    @patch('sys.stdout', new_callable=StringIO)
    def test_normal_show(self, output):
        ndomains = len(self.client.domains)
        args = {}
        args['no_header'] = False
        args['verbose'] = False
        self.domain.show(args)
        domain_list = output.getvalue().split('\n')
        count = len(domain_list) - 1
        self.assertEqual(ndomains, count)

    @patch('sys.stdout', new_callable=StringIO)
    def test_verbose_show(self, output):
        args = {}
        args['no_header'] = False
        args['verbose'] = True
        test_domain = random.randint(0, len(self.client.domains) - 1)
        test_domain = self.client.domains[test_domain]
        self.domain.show(args)
        domain_list = output.getvalue().split('\n')
        domain = ''
        for domain in domain_list:
            if test_domain.base_url in domain:
                break
        domain = domain.split()
        cleaned_domain = []
        for attribute in domain:
            if attribute:
                cleaned_domain.append(attribute)
        self.assertEqual(cleaned_domain[0], test_domain.base_url)
        self.assertEqual(cleaned_domain[1], test_domain.contact_address)
        self.assertEqual(cleaned_domain[2], test_domain.mail_host)
        self.assertEqual(cleaned_domain[3], test_domain.url_host)

    @patch('sys.stdout', new_callable=StringIO)
    def test_no_header(self, output):
        args = {}
        args['no_header'] = True
        args['verbose'] = True
        test_domain = random.randint(0, len(self.client.domains) - 1)
        test_domain = self.client.domains[test_domain]
        self.domain.show(args)
        domain_list = output.getvalue().split('\n')
        line_one = domain_list[0].split()
        self.assertNotEqual(line_one[0], 'Base')
        domain = ''
        for domain in domain_list:
            if test_domain.base_url in domain:
                break
        domain = domain.split()
        cleaned_domain = []
        for attribute in domain:
            if attribute:
                cleaned_domain.append(attribute)
        self.assertEqual(cleaned_domain[0], test_domain.base_url)
        self.assertEqual(cleaned_domain[1], test_domain.contact_address)
        self.assertEqual(cleaned_domain[2], test_domain.mail_host)
        self.assertEqual(cleaned_domain[3], test_domain.url_host)

    def tearDown(self):
        for domain in self.domain_names:
            try:
                self.client.delete_domain(domain)
            except Exception:
                pass
