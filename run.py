import cmd
import ps
from time import sleep
import psutil
from sms_activate import SMSActivate
from config import Config
import re
from database import Database
from enums import *
import os, utility

banner = '''
                                                                                                       
                                                                                                       
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
        new_fotor = ps.start(['python', 'telegram_signup.py', '--log' ,'debug', '-v'])
        process_list.append(new_fotor)
        self.do_log(len(process_list)-1)

    def do_list(self, arg):
        'List of all running accounts'
        print(f'{"PhoneNumber":<20}', f'{"Status":<20}', f'{"Joins":<20}')
        print('=' * 60)

        # Get list of running process https://stackoverflow.com/a/43065994/9850815
        accounts = []
        db = Database()
        # for p in psutil.process_iter():
        #     cmdline = ' '.join(p.cmdline())
        #     if 'join.py' in p.name() or 'join.py' in cmdline:
        #         phone_number = GetPhoneFromCMDLine(cmdline)
        #         accounts.append(phone_number)
        #         joins = db.CountOfJoins(phone_number)
        #         status = TelegramRegisterStats(db.GetStatus(phone_number)).name
        #         print(f'{p.pid:<20}', f'{phone_number:<20}', f'{joins:<20}', f'{status:<20}')

        for file in os.listdir(Config['account_path']):
            if file.endswith(".session"):
                phone_number = file.split('.')[0]
                if utility.ValidatePhone(phone_number):
                    status = db.GetStatus(phone_number)
                    joins = db.CountOfJoins(phone_number)
                    accounts.append({'Phone' : phone_number, 'Status' : status, 'Joins' : joins })
        accounts = utility.SortListOfDict(accounts,'Joins')        
        if accounts is not None:
            for account in accounts:
                status = account['Status']
                if int(status ) not in (TelegramRegisterStats.Ban.value, TelegramRegisterStats.AuthProblem.value):
                    status = TelegramRegisterStats(status).name
                    phone_number = account['Phone']
                    joins = account['Joins']
                    print(f'{phone_number:<20}', f'{status:<20}', f'{joins:<20}')      

        db.Close()

    def do_log(self, arg):
        'Log a joiner'
        ps.tail('logs/join.log',arg)

    def do_login(self, arg):
        'Login to the exist account'
        fotor = ps.start(['python', 'join.py', '--account', str(arg), '--log', 'debug', '-v'])
        process_list.append(fotor)
        self.do_log(arg)

    def do_kill(self, arg):
        'Terminate a process'
        # https://stackoverflow.com/a/17858114/9850815
        try:
            p = psutil.Process(int(arg))
            cmdline = ' '.join(p.cmdline())
            if 'join.py' in cmdline:
                p.terminate()
        except psutil.NoSuchProcess:
            print('No process found with pid %s. Please use proccess id' % arg)

    def do_balance(self, arg):
        'Get sms-activate balance'
        sms = SMSActivate(Config['SMS_Activate_API'])
        print('sms-activate.ru balance is: %s' % sms.Balance())

    def do_register(self, args):
        'Register new number to account database'
        account_info = args.split()
        if len(account_info) == 6:
            phonenumber, country, firstname, family, gender, status = account_info
            db = Database()
            db.NewAccount(phonenumber, country, firstname, family, int(gender))
            db.UpdateStatus(phonenumber, int(status))
            db.Close()
        else:
            print("Use this value => phonenumber country firstname family gender status")

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

def GetPhoneFromCMDLine(cmdline):
    pattern = r'\d{10,}'
    match = re.search(pattern, cmdline)
    if match:
        return match[0]
    else:
        return None



if __name__ == '__main__':
    print(banner)
    FotorShell().cmdloop()