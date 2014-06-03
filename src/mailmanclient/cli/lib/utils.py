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

from hashlib import sha1
from datetime import datetime


class Colorizer():
    " Give colored output on the CLI"

    def warn(self, message):
        print "\033[93m%s\033[0m" % message

    def error(self, message):
        print "\033[91m%s\033[0m" % message

    def confirm(self, message):
        print "\033[92m%s\033[0m" % message,


class Utils(Colorizer):
    """ General utilities to be used across the CLI """

    def get_random_string(self, length):
        """ Returns short random strings, less than 40 bytes in length.

        :param length: Length of the random string to be returned
        :type length: int
        """
        try:
            return sha1(str(datetime.now())).hexdigest()[:length]
        except IndexError:
            raise Exception('Specify length less than 40')
