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
from mailmanclient.cli.core.users import Users, UserException
from mailmanclient.cli.lib.mailman_utils import MailmanUtils


class TestCreateUser(unittest.TestCase):

    utils = MailmanUtils()
    new_users = []

    def setUp(self):
        self.client = self.utils.connect()
        self.users = Users(self.client)
        self.test_user = 'a@' + self.utils.get_random_string(5) + '.org'
        self.new_users.append(self.test_user)
        self.client.create_user(email=self.test_user,
                                password='abcdefgh',
                                display_name='abc')
        self.test_list = self.client.lists[0]
        self.test_list.subscribe(self.test_user)

        # Test if user created else setup fails.
        self.client.get_user(self.test_user)

    def test_normal_create(self):
        args = {}
        new_user = 'a@' + self.utils.get_random_string(5) + '.org'
        self.new_users.append(new_user)
        args['email'] = new_user
        args['password'] = 'abc'
        args['name'] = 'abc'
        self.users.create(args)
        self.assertRaises(UserException, self.users.create, args)

    def test_create_existent_user(self):
        args = {}
        args['email'] = self.test_user
        args['password'] = 'abc'
        args['name'] = 'abc'
        self.assertRaises(UserException, self.users.create, args)

    def tearDown(self):
        for user in self.new_users:
            try:
                u = self.client.get_user(user)
                u.delete()
            except Exception as e:
                print e


class TestSubscription(unittest.TestCase):

    utils = MailmanUtils()
    new_users = []
    domain_list = []

    def setUp(self):
        self.client = self.utils.connect()
        self.users = Users(self.client)

        self.test_domain = self.utils.get_new_domain_name()
        self.domain_list.append(self.test_domain)
        self.client.create_domain(self.test_domain)

        self.test_user = self.utils.get_random_string(8) + '@domain.org'
        self.new_users.append(self.test_user)
        self.client.create_user(email=self.test_user,
                                password='abcdefgh',
                                display_name='abc')
        self.client.get_user(self.test_user)
        domain = self.client.get_domain(self.test_domain)
        self.test_list = (self.utils.get_random_string(8) +
                          '@' + self.test_domain)
        domain.create_list(self.test_list.split('@')[0])

        # Test if user created else setup fails.
        self.client.get_user(self.test_user)

    def test_subscribe_to_list(self):
        print self.test_user
        _list = self.client.get_list(self.test_list)
        nmembers = len(_list.members)
        args = {}
        args['users'] = ['a@b.com', 'b@c.com', 'd@e.com']
        self.new_users.extend(args['users'])
        args['list_name'] = self.test_list
        args['quiet'] = False
        self.users.subscribe(args)
        self.assertEqual(nmembers + 3, len(_list.members))

    def tearDown(self):
        for i in self.new_users:
            try:
                user = self.client.get_user(i)
                user.delete()
            except Exception:
                pass
        for i in self.domain_list:
            try:
                self.client.delete_domain(i)
            except Exception:
                pass
