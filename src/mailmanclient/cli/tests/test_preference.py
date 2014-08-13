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

import unittest
from mailmanclient.cli.core.users import Users, UserException
from mailmanclient.cli.lib.mailman_utils import MailmanUtils


utils = MailmanUtils()
class TestUpdate(unittest.TestCase):

    new_objects = []

    test_user = None
    test_domain = None
    test_list = None
    test_address = None
    test_member = None

    def setUp(self):
        self.client = utils.connect()
        self.test_user = 'a@' + utils.get_random_string(5) + '.com'
        self.test_user = self.client.create_user(self.test_user, display_name = 'a',
                                password='a')
        self.new_objects.append(self.test_user)

        self.test_domain = self.client.create_domain(utils.get_random_string(5)
                                                     + '.org')
        self.new_objects.append(self.test_domain)
        self.test_list = self.test_domain.create_list(utils.get_random_string(5))
        self.new_objects.append(self.test_list)

        self.test_member = self.test_list.subscribe(self.test_user.addresses[0])

        self.test_address = self.test_user.addresses[0]

    def test_global(self):
        pref = self.client.preferences
        pref['receive_list_copy'] = False
        pref.save()
        pref = self.client.preferences
        self.assertFalse(pref['receive_list_copy'])

    def test_user(self):
        pref = self.test_user.preferences
        pref['receive_list_copy'] = False
        pref.save()
        pref = self.test_user.preferences
        self.assertFalse(pref['receive_list_copy'])

    def test_address(self):
        pref = self.test_address.preferences
        pref['receive_list_copy'] = False
        pref.save()
        pref = self.test_address.preferences
        self.assertFalse(pref['receive_list_copy'])

    def test_member(self):
        pref = self.test_member.preferences
        pref['receive_list_copy'] = False
        pref.save()
        pref = self.test_member.preferences
        self.assertFalse(pref['receive_list_copy'])

    def tearDown(self):
        for obj in self.new_objects:
            try:
                if type(obj).__name__ == '_Domain': 
                    self.client.delete_domain(obj.base_url)
                else:
                    obj.delete()
            except:
                pass
