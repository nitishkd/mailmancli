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
import zipfile
from mailman.config import config
from mailmanclient.cli.lib.utils import Utils
from mailmanclient import MailmanConnectionError


utils = Utils()


class MiscException(Exception):
    """ Exceptions for miscellaneous actions """
    pass


class Misc():
    """ Miscellaneous actions """
    def __init__(self, client):
        self. client = client

    def backup(self, args):
        try:
            self.client.lists
            utils.error('Please stop mailman runner before backup')
            return
        except MailmanConnectionError:
            utils.warn('Performing backup action')
        config.load()
        vardir = config.paths['VAR_DIR']
        output = args['output']
        if not output.endswith('.zip'):
            output += '.zip'
        relroot = os.path.abspath(os.path.join(vardir, os.pardir))
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(vardir):
                z.write(root, os.path.relpath(root, relroot))
                for f in files:
                    filename = os.path.join(root, f)
                    if os.path.isfile(filename):
                        arcname = os.path.join(os.path.relpath(root, relroot),
                                               f)
                        z.write(filename, arcname)

    def restore(self, args):
        try:
            self.client.lists
            utils.error('Please stop mailman runner before restore')
            return
        except MailmanConnectionError:
            utils.warn('Performing restore action')
        config.load()
        vardir = config.paths['VAR_DIR']
        backup = args['backup']
        if os.path.exists(vardir):
            utils.confirm('The existing var_dir will be replaced.Continue?[y/n]')
            confirm = raw_input()
            if not confirm == 'y':
                return
        vardir += '/../'
        with zipfile.ZipFile(backup) as zf:
            zf.extractall(vardir)
