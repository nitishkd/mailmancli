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
from mock import patch
from urllib2 import HTTPError
from StringIO import StringIO
try:
    from core.lists import Lists, ListException
    from core.domains import DomainException
except:
    sys.path = [os.path.abspath(os.path.dirname(__file__)) +
                '/../../cli/'] + sys.path
    from core.domains import DomainException
from lib.mailman_utils import MailmanUtils


class TestCreateList(unittest.TestCase):

    domain_names = []
    utils = MailmanUtils()

    def setUp(self):
        self.client = self.utils.connect()
        self._list = Lists(self.client)
        self.test_domain = self.utils.get_new_domain_name()
        self.domain_names.append(self.test_domain)
        self.client.create_domain(self.test_domain)

        # Raise exception if domain create falied.
        self.domain = self.client.get_domain(self.test_domain)

    def test_normal_create(self):
        args = {}
        list_name = self.utils.get_random_string(5)
        list_name += '@' + self.test_domain
        args['list'] = list_name
        self._list.create(args)

    def test_create_existent_list(self):
        list_name = self.utils.get_random_string(5)
        self.domain.create_list(list_name)
        args = {}
        list_name += '@' + self.test_domain
        args['list'] = list_name
        self.assertRaises(ListException, self._list.create, args)

    def test_invalid_fqdn_create(self):
        test_list = self.utils.get_random_string(5)
        invalid_name_1 = test_list + '@'
        invalid_name_2 = '@' + self.test_domain
        invalid_name_3 = (test_list + '@' +
                          self.utils.get_new_domain_name())
        invalid_name_4 = self.test_domain
        args = {}
        args['list'] = invalid_name_1
        self.assertRaises(ListException, self._list.create, args)
        args['list'] = invalid_name_2
        self.assertRaises(ListException, self._list.create, args)
        args['list'] = invalid_name_3
        self.assertRaises(DomainException, self._list.create, args)
        args['list'] = invalid_name_4
        self.assertRaises(ListException, self._list.create, args)

    def tearDown(self):
        for domain in self.domain_names:
            try:
                self.client.delete_domain(domain)
            except Exception:
                pass


class TestShowList(unittest.TestCase):

    domain_names = []
    utils = MailmanUtils()

    def setUp(self):
        self.client = self.utils.connect()
        self._list = Lists(self.client)
        self.test_domain = self.utils.get_new_domain_name()
        self.test_list = self.utils.get_random_string(5)
        self.domain_names.append(self.test_domain)
        self.client.create_domain(self.test_domain)

        # Raise exception if domain create falied.
        self.domain = self.client.get_domain(self.test_domain)
        self.domain.create_list(self.test_list)

    @patch('sys.stdout', new_callable=StringIO)
    def test_normal_show(self, output):
        nlists = len(self.client.lists)
        args = {}
        args['no_header'] = False
        args['verbose'] = False
        args['domain'] = None
        self._list.show(args)
        mlist_list = output.getvalue().split('\n')
        count = len(mlist_list) - 1
        self.assertEqual(nlists, count)

    @patch('sys.stdout', new_callable=StringIO)
    def test_filter_show(self, output):
        nlists = len(self.domain.lists)
        args = {}
        args['no_header'] = False
        args['verbose'] = False
        args['domain'] = self.test_domain
        self._list.show(args)
        mlist_list = output.getvalue().split('\n')
        count = len(mlist_list) - 1
        self.assertEqual(nlists, count)

    @patch('sys.stdout', new_callable=StringIO)
    def test_verbose_show(self, output):
        args = {}
        args['no_header'] = False
        args['verbose'] = True
        args['domain'] = None
        self._list.show(args)
        mlists = output.getvalue().split('\n')
        test_list = '%s@%s' % (self.test_list, self.test_domain)
        mlist = ''
        for mlist in mlists:
            if test_list in mlist:
                break
        mlist = mlist.split()
        cleaned_list = []
        for attribute in mlist:
            if attribute:
                cleaned_list.append(attribute)
        mlist = self.client.get_list(test_list)
        self.assertEqual(cleaned_list[0], mlist.list_id)
        self.assertEqual(cleaned_list[1], mlist.list_name)
        self.assertEqual(cleaned_list[2], mlist.mail_host)
        self.assertEqual(cleaned_list[3], mlist.display_name)
        self.assertEqual(cleaned_list[4], mlist.fqdn_listname)

    @patch('sys.stdout', new_callable=StringIO)
    def test_filter_verbose_show(self, output):
        args = {}
        args['no_header'] = False
        args['verbose'] = True
        args['domain'] = self.test_domain
        self._list.show(args)
        mlists = output.getvalue().split('\n')
        mlist = ''
        test_list = '%s@%s' % (self.test_list, self.test_domain)
        for mlist in mlists:
            if test_list in mlist:
                break
        mlist = mlist.split()
        cleaned_list = []
        for attribute in mlist:
            if attribute:
                cleaned_list.append(attribute)
        mlist = self.client.get_list(test_list)
        self.assertEqual(cleaned_list[0], mlist.list_id)
        self.assertEqual(cleaned_list[1], mlist.list_name)
        self.assertEqual(cleaned_list[2], mlist.mail_host)
        self.assertEqual(cleaned_list[3], mlist.display_name)
        self.assertEqual(cleaned_list[4], mlist.fqdn_listname)

    @patch('sys.stdout', new_callable=StringIO)
    def test_no_header(self, output):
        args = {}
        args['no_header'] = False
        args['verbose'] = True
        args['domain'] = None
        self._list.show(args)
        mlists = output.getvalue().split('\n')
        line_one = mlists[0].split()
        self.assertNotEqual(line_one[0], 'Base')
        mlist = ''
        for mlist in mlists:
            if self.test_list in mlist:
                break
        mlist = mlist.split()
        cleaned_list = []
        for attribute in mlist:
            if attribute:
                cleaned_list.append(attribute)
        mlist = self.client.get_list('%s@%s' % (self.test_list,
                                                self.test_domain))
        self.assertEqual(cleaned_list[0], mlist.list_id)
        self.assertEqual(cleaned_list[1], mlist.list_name)
        self.assertEqual(cleaned_list[2], mlist.mail_host)
        self.assertEqual(cleaned_list[3], mlist.display_name)
        self.assertEqual(cleaned_list[4], mlist.fqdn_listname)

    def tearDown(self):
        for domain in self.domain_names:
            try:
                self.client.delete_domain(domain)
            except Exception:
                pass


class TestDeleteList(unittest.TestCase):

    domain_names = []
    utils = MailmanUtils()

    def setUp(self):
        self.client = self.utils.connect()
        self._list = Lists(self.client)
        self.test_domain = self.utils.get_new_domain_name()
        self.test_list = self.utils.get_random_string(5)
        self.domain_names.append(self.test_domain)
        self.client.create_domain(self.test_domain)

        # Raise exception if domain create falied.
        self.domain = self.client.get_domain(self.test_domain)
        self.domain.create_list(self.test_list)

    def test_normal_delete(self):
        new_list = self.utils.get_random_string(5)
        self.domain.create_list(new_list)
        args = {}
        args['list'] = '%s@%s' % (new_list, self.test_domain)
        with patch('__builtin__.raw_input', return_value='y'):
            args['yes'] = True
            self._list.delete(args)
        self.assertRaises(HTTPError, self.client.get_list, args['list'])

    def test_delete_cancel(self):
        new_list = self.utils.get_random_string(5)
        self.domain.create_list(new_list)
        args = {}
        args['list'] = '%s@%s' % (new_list, self.test_domain)
        with patch('__builtin__.raw_input', return_value='n'):
            args['yes'] = False
            self._list.delete(args)
        self.assertRaises(HTTPError, self.domain.create_list, args['list'])

    def test_delete_invalid_confirm(self):
        new_list = self.utils.get_random_string(5)
        self.domain.create_list(new_list)
        args = {}
        args['list'] = '%s@%s' % (new_list, self.test_domain)
        with patch('__builtin__.raw_input', return_value='no'):
            self.assertRaises(Exception, self._list.delete, args)

    def test_delete_without_confirm(self):
        new_list = self.utils.get_random_string(5)
        self.domain.create_list(new_list)
        args = {}
        args['list'] = '%s@%s' % (new_list, self.test_domain)
        args['yes'] = True
        self._list.delete(args)
        self.assertRaises(HTTPError, self.client.get_list, args['list'])

    def tearDown(self):
        for domain in self.domain_names:
            try:
                self.client.delete_domain(domain)
            except Exception:
                pass
