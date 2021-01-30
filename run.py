import cmd
import ps

class FotorShell(cmd.Cmd):
    intro = 'Welcome to the Fotor shell.'
    prompt = '(Fotor)'

    def do_new(self, arg):
        'Create new telegram account'
        ps.start('python join.py --log debug -v')

    def do_exit(self, arg):
        'Exit from shell'
        exit()


if __name__ == '__main__':
    FotorShell().cmdloop()