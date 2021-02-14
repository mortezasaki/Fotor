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
import datetime

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




class FotorShell(cmd.Cmd):
    intro = 'Welcome to the Fotor shell.'
    prompt = 'Fotor: '

    def do_new(self, arg):
        'Create new telegram account'
        new_fotor = ps.start(['python', 'telegram_signup.py', '--log' ,'debug', '-v'])
        self.do_log(None, register_log = True)

    def do_list(self, arg):
        'List of all running accounts'
        print(f'{"PhoneNumber":<20}', f'{"Status":<20}', f'{"Joins":<20}', f'{"FloowWait":<20}')
        print('=' * 80)


        showed = [] # a list that uses for which account type was showed
        if arg == 'ban':
            showed = [TelegramRegisterStats.Succesfull.value, TelegramRegisterStats.AuthProblem.value, TelegramRegisterStats.FloodWait.value,
                        TelegramRegisterStats.HasPassword.value, TelegramRegisterStats.Running.value, TelegramRegisterStats.Stop.value,
                        TelegramRegisterStats.ToMany.value]
        elif arg =='problem':
            showed = [TelegramRegisterStats.Succesfull.value, TelegramRegisterStats.Ban.value, TelegramRegisterStats.FloodWait.value,
                        TelegramRegisterStats.Running.value, TelegramRegisterStats.Stop.value, TelegramRegisterStats.ToMany.value]
        elif arg == 'running':
            showed = [TelegramRegisterStats.Succesfull.value, TelegramRegisterStats.AuthProblem.value, TelegramRegisterStats.FloodWait.value,
                        TelegramRegisterStats.HasPassword.value, TelegramRegisterStats.Ban.value, TelegramRegisterStats.Stop.value, TelegramRegisterStats.ToMany.value]
        elif arg == 'many': # To fix Issue 18
            showed = [TelegramRegisterStats.Succesfull.value, TelegramRegisterStats.AuthProblem.value, TelegramRegisterStats.FloodWait.value,
                        TelegramRegisterStats.HasPassword.value, TelegramRegisterStats.Ban.value, TelegramRegisterStats.Stop.value,
                        TelegramRegisterStats.Running.value]                    
        else:
            showed = [TelegramRegisterStats.Ban.value, TelegramRegisterStats.AuthProblem.value, TelegramRegisterStats.HasPassword.value,
                        TelegramRegisterStats.ToMany.value]

        accounts = []
        db = Database()

        try:
            for file in os.listdir(Config['account_path']):
                if file.endswith(".session"):
                    phone_number = file.split('.')[0]
                    if utility.ValidatePhone(phone_number):
                        db.NewAccount(phone_number, 'Test', 'Test', 'Test', 0)
                        status = db.GetStatus(phone_number)
                        joins = db.CountOfJoins(phone_number)
                        accounts.append({'Phone' : phone_number, 'Status' : status, 'Joins' : joins })
            accounts = utility.SortListOfDict(accounts,'Joins')        
            if accounts is not None:
                for account in accounts:
                    status = account['Status']
                    if int(status ) not in showed:
                        # Fix https://app.gitkraken.com/glo/view/card/c83bdb72da984df28d6a84b9994ac6cd
                        # Fix when account not runnig but in database has running. Change status to stop
                        if int(status) == TelegramRegisterStats.Running.value:
                            process = GetListOfAllProccess()
                            running = False
                            for p in process:
                                if p['Phone'] == account['Phone']:
                                    running = True
                                    break
                            if not running:
                                status = TelegramRegisterStats.Stop.value

                        # نمایش فلود ویت در لیست اگر در دیتابیس برای اکانت ثبت شده باشد
                        floodWait = str(datetime.timedelta(seconds=0))
                        if int(status) == TelegramRegisterStats.FloodWait.value:
                            flood = db.GetFloodWait(account['Phone'])
                            if len(flood) == 2:
                                _time = datetime.datetime.strptime(flood[0], '%Y-%m-%d %H:%M:%S.%f')
                                seconds_passed = (datetime.datetime.now() - _time ).total_seconds()
                                if seconds_passed < flood[1]:
                                    # Fix Issue 10
                                    seconds_passed = flood[1] - seconds_passed
                                    floodWait ='{:02}:{:02}:{:02}'.format(int(seconds_passed // 3600), int(seconds_passed % 3600 // 60), int(seconds_passed % 60))
                                else:
                                    status = TelegramRegisterStats.Stop.value

                        status = TelegramRegisterStats(status).name
                            
                        phone_number = account['Phone']
                        joins = account['Joins']
                        print(f'{phone_number:<20}', f'{status:<20}', f'{joins:<20}', f'{floodWait:<20}') 
        except FileNotFoundError:
            print('No such file or directory')

        db.Close()

    # Display system statistics. Issue #3
    def do_statistics(self, arg):
        statistics = '''
Fotor Statistics
=====================
Accounts = {0}
---------------------
Running = {1}
FloodWait = {2}
Stop = {3}
ToMany = {8}
Ban = {4}
Has Password = {5}
Has Problem = {6}
----------------------
Joins = {7}
'''

        db = Database()
        accounts = db.Count('Select * from account', ())
        running = db.Count('Select * from account where status = ?',(TelegramRegisterStats.Running.value,))
        flood = db.Count('Select * from account where status = ?',(TelegramRegisterStats.FloodWait.value,))
        ban = db.Count('Select * from account where status = ?',(TelegramRegisterStats.Ban.value,))
        hasPassword = db.Count('Select * from account where status = ?',(TelegramRegisterStats.HasPassword.value,))
        problem = db.Count('Select * from account where status = ?',(TelegramRegisterStats.AuthProblem.value,))
        toMany = db.Count('Select * from account where status = ?',(TelegramRegisterStats.ToMany.value,))

        # Solution for issue 14
        for acc in db.GetAccounts():
            status = acc[6]
            if status == TelegramRegisterStats.FloodWait.value:
                _time = datetime.datetime.strptime(acc[7], '%Y-%m-%d %H:%M:%S.%f')
                seconds_passed = (datetime.datetime.now() - _time ).total_seconds()
                if seconds_passed > acc[8]:
                    flood-=1

        stop = accounts - (running+flood+ban+hasPassword+problem+toMany) # fix issue #9

        joins = db.Count('Select * from joins', ())


        statistics = statistics.format(accounts, running, flood, stop, ban, hasPassword, problem, joins, toMany)
        print(statistics)

    def do_log(self, arg, register_log = False):
        'Log a joiner'
        if register_log or arg == 'register':
            ps.tail('logs/register.log', match=False)
        else:
            ps.tail('logs/join.log',arg)

    def do_login(self, arg):
        'Login to the exist account'
        proccess = GetListOfAllProccess()
        running = True
        for p in proccess:
            if arg == p['Phone']:
                print('%s is running.' % arg)
                running = False
                break
        if running:
            fotor = ps.start(['python', 'join.py', '--account', str(arg), '--log', 'debug', '-v'])
            self.do_log(arg)

    def do_auto(self, arg):
        'Automate Create account and join to channel with limitation'
        if arg == 'stop':
                for p in psutil.process_iter():
                    if 'auto.py' in p.cmdline():
                        p.terminate()
                        print('Automation stoped')
                        break
        elif arg == '':
            started = False
            for p in psutil.process_iter():
                if 'auto.py' in p.cmdline():
                    started = True
                    print('Automation has been started')
                    break

            if not started:
                ps.start(['python', 'auto.py'])
                print('Start automation with account limitation %s' % Config['limit_account'])

    def do_kill(self, arg):
        'Terminate a process'
        # https://stackoverflow.com/a/17858114/9850815
        proccess = GetListOfAllProccess()
        found = False
        for p in proccess:
            if p['Phone'] == arg:
                found = True
                try :
                    p = psutil.Process(p['PID'])
                    p.terminate()
                    db = Database()
                    db.UpdateStatus(arg, TelegramRegisterStats.Stop.value)
                    print('Account with phone number %s was stoped' % arg)
                except psutil.NoSuchProcess:
                    print('No process found with pid %s. Please use proccess id. please try again' % p['PID'])
                break
        if not found:
            print('No account found with number %s' % arg)
                
    def do_delete(self, phonenumber):
        self.do_kill(phonenumber)
        db = Database()
        if utility.ValidatePhone(phonenumber) and db.DeleteAccount(phonenumber):
            file_path = '{0}{1}.session'.format(Config['account_path'], phonenumber)
            if os.path.exists(file_path):
                os.remove(file_path)
            print('%s account has been deleted.' % phonenumber)
        else:
            print('Value error')
        db.Close()


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

    def do_banner(self,arg):
        print(banner)

    def do_exit(self, arg):
        'Exit from shell'
        exit()

    def do_createdb(self, arg):
        'Initial create database.'
        if not os.path.exists('data.db'):
            db = Database()
            db.Create()
            db.Close()
        else:
            print('Database exist')

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

# Get list of running process https://stackoverflow.com/a/43065994/9850815
def GetListOfAllProccess():
    accounts = []
    for p in psutil.process_iter():
        cmdline = ' '.join(p.cmdline())
        pattern = r'\d{10,}'
        if 'join.py' in cmdline and re.search(pattern, cmdline):
            phone_number = GetPhoneFromCMDLine(cmdline)
            process = {'PID' : p.pid, 'Phone' : phone_number}
            accounts.append(process)
    
    return accounts



if __name__ == '__main__':
    print(banner)
    if not os.path.exists('logs/'):
        os.mkdir('logs')
    FotorShell().cmdloop()