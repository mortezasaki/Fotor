import cmd
import ps
from time import sleep
import psutil


def ProccessExist(pid):
    return pid in (p.pid for p in psutil.process_iter())

class FotorShell(cmd.Cmd):
    intro = 'Welcome to the Fotor shell.'
    prompt = 'Fotor: '

    def do_new(self, arg):
        'Create new telegram account'
        new_fotor = ps.start('python join.py --log debug -v')
        print('Prees CTRL+C to exit')
        sleep(1)
        while ps.is_running(new_fotor):
            try:
                log = ps.read(new_fotor)
                if len(log) > 0:
                    print(log)
            except :
                break


    def do_exit(self, arg):
        'Exit from shell'
        exit()

    # Handle when press enter do nothing https://stackoverflow.com/a/21066546/9850815
    def emptyline(self):
         pass



if __name__ == '__main__':
    FotorShell().cmdloop()