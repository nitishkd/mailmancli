from argparse import ArgumentParser
from mailmanclient._client import MailmanConnectionError
from core.lists import Lists


class CmdParser():
    def __init__(self, command):
        parser = ArgumentParser(description='Mailman Command Tools')
        self.initialize_options(parser)
        self.arguments = vars(parser.parse_args())

    def initialize_options(self, parser):
        parser.add_argument('instance', help='Specify instance',
                            choices=['list', 'domain', 'user'])
        parser.add_argument('action', help='Specify an action',
                            choices=['create', 'delete', 'list'])
        parser.add_argument('-l', '--listname', help='Name of the list')
        parser.add_argument('-d', '--domainname', help='Name of the domain')
        parser.add_argument('-u', '--username', help='Name of the user')
        parser.add_argument('--host', help='REST API host address',
                            default='http://127.0.0.1')
        parser.add_argument('--port', help='REST API host port',
                            default='8001')
        parser.add_argument('--restuser', help='REST API username',
                            default='restadmin')
        parser.add_argument('--restpass', help='REST API password',
                            default='restpass')

    def operate_list(self):
        l = Lists()
        try:
            l.connect(host=self.arguments['host'], port=self.arguments['port'],
                      username=self.arguments['restuser'],
                      password=self.arguments['restpass'])
        except MailmanConnectionError:
            print 'Connection to REST API failed'
            exit(1)
        action = self.arguments['action']
        if action == 'create':
            l.create(self.arguments['domainname'],
                     self.arguments['listname'])

    def operate_domain(self):
        print "Operate Domains"

    def run(self):
        method_name = 'operate_' + self.arguments['instance']
        method = getattr(self, method_name)
        method()
