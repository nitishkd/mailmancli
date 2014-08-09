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

import random
import unittest
from mock import patch
from urllib2 import HTTPError
from StringIO import StringIO
from mailmanclient.cli.core.domains import Domains, DomainException
from mailmanclient.cli.lib.mailman_utils import MailmanUtils


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


class TestShowDomain(unittest.TestCase):

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
        args['csv'] = None
        args['domain'] = None
        self.domain.show(args)
        domain_list = output.getvalue().split('\n')
        count = len(domain_list) - 1
        self.assertEqual(ndomains, count)

    @patch('sys.stdout', new_callable=StringIO)
    def test_verbose_show(self, output):
        args = {}
        args['no_header'] = False
        args['verbose'] = True
        args['csv'] = None
        args['domain'] = None
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
        args['csv'] = None
        args['verbose'] = True
        args['domain'] = None
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
        with patch('__builtin__.raw_input', return_value='y'):
            args['yes'] = True
            self.domain.delete(args)
        self.assertRaises(HTTPError, self.client.get_domain, new_domain)

    def test_delete_cancel(self):
        new_domain = self.utils.get_new_domain_name()
        self.domain_names.append(new_domain)
        self.client.create_domain(new_domain)
        args = {}
        args['domain'] = new_domain
        with patch('__builtin__.raw_input', return_value='n'):
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
        with patch('__builtin__.raw_input', return_value='no'):
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
