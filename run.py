import cmd
import ps
from time import sleep


process_list = []
class FotorShell(cmd.Cmd):
    intro = 'Welcome to the Fotor shell.'
    prompt = 'Fotor: '

    def do_new(self, arg):
        'Create new telegram account'
        # new_fotor = ps.start('python join.py --log debug -v')
        process_list.append(ps.start(['python', 'join.py', '--log' ,'debug', '-v']))
        print('Prees CTRL+C to exit')
        sleep(2)
        while ps.is_running(process_list[-1]):
            try:
                process_log = ps.read(process_list[-1])
                if len(process_log) > 0:
                    print(process_log)
            except :
                break

    def do_list(self, arg):
        'List of all running accounts'
        print(f'{"Index":<10}', f'{"ProcessId":<10}')
        for id, process in enumerate(process_list):
            if ps.is_running(process):
                print(f'{id:<10}', f'{process.pid:<10}')

            


    def do_exit(self, arg):
        'Exit from shell'
        exit()

    # Handle when press enter do nothing https://stackoverflow.com/a/21066546/9850815
    def emptyline(self):
         pass



if __name__ == '__main__':
    FotorShell().cmdloop()