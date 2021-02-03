import cmd
import ps
from time import sleep
import psutil


logo = '''
                                                                                                       
                                                                                                       
FFFFFFFFFFFFFFFFFFFFFF     OOOOOOOOO     TTTTTTTTTTTTTTTTTTTTTTT     OOOOOOOOO     RRRRRRRRRRRRRRRRR   
F::::::::::::::::::::F   OO:::::::::OO   T:::::::::::::::::::::T   OO:::::::::OO   R::::::::::::::::R  
F::::::::::::::::::::F OO:::::::::::::OO T:::::::::::::::::::::T OO:::::::::::::OO R::::::RRRRRR:::::R 
FF::::::FFFFFFFFF::::FO:::::::OOO:::::::OT:::::TT:::::::TT:::::TO:::::::OOO:::::::ORR:::::R     R:::::R
  F:::::F       FFFFFFO::::::O   O::::::OTTTTTT  T:::::T  TTTTTTO::::::O   O::::::O  R::::R     R:::::R
  F:::::F             O:::::O     O:::::O        T:::::T        O:::::O     O:::::O  R::::R     R:::::R
  F::::::FFFFFFFFFF   O:::::O     O:::::O        T:::::T        O:::::O     O:::::O  R::::RRRRRR:::::R 
  F:::::::::::::::F   O:::::O     O:::::O        T:::::T        O:::::O     O:::::O  R:::::::::::::RR  
  F:::::::::::::::F   O:::::O     O:::::O        T:::::T        O:::::O     O:::::O  R::::RRRRRR:::::R 
  F::::::FFFFFFFFFF   O:::::O     O:::::O        T:::::T        O:::::O     O:::::O  R::::R     R:::::R
  F:::::F             O:::::O     O:::::O        T:::::T        O:::::O     O:::::O  R::::R     R:::::R
  F:::::F             O::::::O   O::::::O        T:::::T        O::::::O   O::::::O  R::::R     R:::::R
FF:::::::FF           O:::::::OOO:::::::O      TT:::::::TT      O:::::::OOO:::::::ORR:::::R     R:::::R
F::::::::FF            OO:::::::::::::OO       T:::::::::T       OO:::::::::::::OO R::::::R     R:::::R
F::::::::FF              OO:::::::::OO         T:::::::::T         OO:::::::::OO   R::::::R     R:::::R
FFFFFFFFFFF                OOOOOOOOO           TTTTTTTTTTT           OOOOOOOOO     RRRRRRRR     RRRRRRR
                                                                                                       
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
'''




process_list = []
class FotorShell(cmd.Cmd):
    intro = 'Welcome to the Fotor shell.'
    prompt = 'Fotor: '

    def do_new(self, arg):
        'Create new telegram account'
        new_fotor = ps.start(['python', 'join.py', '--log' ,'debug', '-v'])
        process_list.append(new_fotor)
        self.do_log(len(process_list)-1)

    def do_list(self, arg):
        'List of all running accounts'
        print(f'{"ProcessId":<10}', f'{"ProcessName":<10}')

        # Get list of running process https://stackoverflow.com/a/43065994/9850815
        for p in psutil.process_iter():
            cmdline = ' '.join(p.cmdline())
            if 'join.py' in p.name() or 'join.py' in cmdline:
                print(f'{p.pid:<10}', f'{cmdline:<10}')

    def do_log(self, arg):
        'Log a joiner'
        try:
            arg = int(arg)
            while ps.is_running(process_list[arg]):
                try:
                    ps.tail('logs/%s.log' % process_list[arg].pid)
                except KeyboardInterrupt:
                    break
        except IndexError:
            print('Index error')

    def do_login(self, arg):
        'Login to the exist account'
        fotor = ps.start(['python', 'join.py', '--account', str(arg), '--log', 'debug', '-v'])
        process_list.append(fotor)
        self.do_log(len(process_list)-1)


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
    print(logo)
    FotorShell().cmdloop()