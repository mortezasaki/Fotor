import cmd
import ps
from time import sleep

process_list = []
class FotorShell(cmd.Cmd):
    intro = 'Welcome to the Fotor shell.'
    prompt = 'Fotor: '

    def do_new(self, arg):
        'Create new telegram account'
        new_fotor = ps.start(['python', 'join.py', '--log' ,'debug', '-v'])
        process_list.append(new_fotor)
        # print('Prees CTRL+C to exit')
        # sleep(1)
        # while ps.is_running(new_fotor):
        #     try:
        #         ps.tail('logs/%s.log' % new_fotor.pid)
        #         # process_output, _ =  new_fotor.communicate()
        #         # process_log = ps.read(new_fotor)
        #         # if process_log is not None:
        #         #     print(process_log)
        #     except KeyboardInterrupt:
        #         break

    def do_list(self, arg):
        'List of all running accounts'
        print(f'{"Index":<10}', f'{"ProcessId":<10}')
        for id, process in enumerate(process_list):
            if ps.is_running(process):
                print(f'{id:<10}', f'{process.pid:<10}')

    def do_log(self, arg):
        arg = int(arg)
        while ps.is_running(process_list[arg]):
            try:
                ps.tail('logs/%s.log' % process_list[arg].pid)
                # process_output, _ =  new_fotor.communicate()
                # process_log = ps.read(new_fotor)
                # if process_log is not None:
                #     print(process_log)
            except KeyboardInterrupt:
                return True
            


    def do_exit(self, arg):
        'Exit from shell'
        exit()

    # Handle when press enter do nothing https://stackoverflow.com/a/21066546/9850815
    def emptyline(self):
         pass

    def cmdloop(self, intro=None):
        print(self.intro)
        while True:
            try:
                super(FotorShell, self).cmdloop(intro="")
                break
            except KeyboardInterrupt:
                print("^C")        



if __name__ == '__main__':
    FotorShell().cmdloop()