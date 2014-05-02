from cmd import Cmd


class Shell(Cmd):
    intro = 'Mailman Command Line Interface v1.0'
    prompt = '>>>'

    def do_EOF(self, args):
        print
        print 'Bye!'
        exit(0)
