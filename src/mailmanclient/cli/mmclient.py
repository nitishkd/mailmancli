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

import sys
from lib.utils import Utils
from client.shell import Shell
from client.cmdparser import CmdParser

def main():
    try:
        sys.argv[1]
        utils = Utils()
        arguments = None
        try:
            arguments = utils.stem(sys.argv)
        except IndexError:
            pass
        c = CmdParser(arguments)
        c.run()
    except IndexError:
        s = Shell()
        s.initialize()
        s.cmdloop()


if __name__ == '__main__':
    main()
