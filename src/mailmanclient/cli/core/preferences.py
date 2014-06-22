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

from lib.utils import Utils


utils = Utils()


class PreferenceException(Exception):
    pass


class Preferences():
    """Preferences related actions."""

    def __init__(self, client):
        self.client = client

        # Tests if connection OK else raise exception
        preferences = self.client.preferences
        del preferences

    def get_scope_object(self, scope, args):
        scope_object = None
        try:
            if scope == 'global':
                scope_object = self.client
            elif scope == 'user':
                scope_object = self.client.get_user(args['email'])
            elif scope == 'member':
                scope_object = self.client.get_member(args['list'],
                                                      args['email'])
            else:
                scope_object = self.client.get_address(args['email'])
        except:
            raise PreferenceException('%s not found %s' % scope.capitalize())
        return scope_object

    def update(self, args):
        """Update a preference specified by the `key` to `value`
           Preferences can be set at a global, user, address or at
           a member level.
        """
        scope = args['update_scope']
        scope_object = self.get_scope_object(scope, args)
        preferences = None
        key = args['key']
        value = args['value']
        preferences = scope_object.preferences
        if type(preferences[key]).__name__ in ('bool', 'NoneType'):
            value = value.lower().strip()
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
            else:
                raise PreferenceException('Invalid value for preference.'
                                          'Expected values : True/False')
        try:
            preferences[key] = value
            preferences.save()
        except Exception:
            raise PreferenceException('Saving Preference Failed')

    def show(self, args):
        """Given a preference key, and a specific object, print
           the current value of the preference for that object."""
        scope = args['show_scope']
        scope_object = self.get_scope_object(scope, args)
        preferences = None
        key = args['key']
        preferences = scope_object.preferences
        print str(preferences[key])
