import cmd
import ps
from time import sleep

class FotorShell(cmd.Cmd):
    intro = 'Welcome to the Fotor shell.'
    prompt = 'Fotor: '

    def do_new(self, arg):
        'Create new telegram account'
        new_fotor = ps.start('python join.py --log debug -v')
        print('Prees CTRL+C to exit')
        while True:
            try:
                print(ps.read(new_fotor))
                sleep(.5)
            except :
                break

    # Handle when press enter do nothing https://stackoverflow.com/a/21066546/9850815
    def do_exit(self, arg):
        'Exit from shell'
        exit()

    def emptyline(self):
         pass



if __name__ == '__main__':
    FotorShell().cmdloop()