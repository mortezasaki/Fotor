# For Issue 7

import psutil
import re
import os
from config import Config
from enums import *
from database import Database
import sys
import utility
import ps
import random
from time import sleep
import datetime
import logging
from pytz import timezone, utc
import signal

# Use custom timezone in logging https://stackoverflow.com/a/45805464/9850815
def customTime(*args):
    try:
        utc_dt = utc.localize(datetime.datetime.utcnow())
        my_tz = timezone("Asia/Tehran")
        converted = utc_dt.astimezone(my_tz)
        return converted.timetuple() 
    except AttributeError:
        return None

    
def LogInit(phone_number):
    # output log on stdout https://stackoverflow.com/a/14058475/9850815
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_file_name = 'logs/auto.log'

    logging.basicConfig(filename=log_file_name, filemode="a", level=logging.INFO,
        format = '%(asctime)s - {0} - %(message)s'.format(phone_number), datefmt="%Y-%m-%d %H:%M:%S") 
    
    logging.Formatter.converter = customTime   

def GetPhoneFromCMDLine(cmdline):
    pattern = r'\d{10,}'
    match = re.search(pattern, cmdline)
    if match:
        return match[0]
    else:
        return None

def GetJoinProcess():
    process = []
    try:
        for p in psutil.process_iter():
            try:
                cmdline = ' '.join(p.cmdline())
                pattern = r'\d{10,}'
                if 'join.py' in cmdline and re.search(pattern, cmdline):
                    phone_number = GetPhoneFromCMDLine(cmdline)
                    process.append(phone_number)
            except psutil.NoSuchProcess:
                continue
    except KeyboardInterrupt: # Fix issue 11
        pass        
    
    return process

# for issue 16
def CheckLimitation():
    db = Database()
    limit = Config['account_per_day']
    accounts = db.GetAccounts()
    if accounts is None: # Fix issue 21
        logging.info('Cant connect to database be sure that data.db exist or execude `createdb` command')
        sleep(1)
        sys.exit()
    count_of_account_created_today = 0

    for account in accounts:
        _time = account[6]
        try:
            _time = datetime.datetime.strptime(_time, '%Y-%m-%d %H:%M:%S.%f')
            if datetime.datetime.today().date() == _time.date():
                count_of_account_created_today+=1
        except TypeError:
            continue
    if count_of_account_created_today < limit:
        return True
    return False

def GetSignUpProcess():
    process = []
    try:
        for p in psutil.process_iter():
            try:
                cmdline = ' '.join(p.cmdline())
                pattern = r'\d{10,}'
                if 'telegram_signup.py' in cmdline:
                    process.append(p)
            except psutil.NoSuchProcess:
                continue
    except KeyboardInterrupt: # Fix issue 11
        pass
    
    return process    

def main():
    if not os.path.exists(Config['account_path']):
        os.mkdir(Config['account_path'])
    limit_account = Config['limit_account']
    while True:
        process = GetJoinProcess()
        if len(process) < limit_account:
            accounts = []
            db = Database()
            try:
                for file in os.listdir(Config['account_path']):
                    logging.info('Get config files...')
                    # fix load account for join when sign up not complated
                    try:
                        file_name = '%s%s' %(Config['account_path'], file)
                        if not os.path.exists(file_name):
                            continue
                        file_creation = os.path.getctime(file_name)
                        file_creation = datetime.datetime.fromtimestamp(file_creation)
                        diff = (datetime.datetime.now() - file_creation).total_seconds() / 60.0 
                        if file.endswith(".session") and diff > 2:
                            phone_number = file.split('.')[0]
                            if utility.ValidatePhone(phone_number):
                                status = db.GetStatus(phone_number)
                                accounts.append({'Phone' : phone_number, 'Status' : status})
                    except FileNotFoundError:
                        logging.info('No such file or directory')
                        continue
                    except AttributeError: # Fix issue 20
                        continue
                
                stoped_accounts = []
                logging.info('Get ready accounts...')
                if accounts is not None and len(accounts) > 0:
                    for account in accounts:
                        logging.info('Loop in accounts')
                        status = account['Status']
                        showed = [TelegramRegisterStats.Ban.value, TelegramRegisterStats.AuthProblem.value,
                                    TelegramRegisterStats.HasPassword.value, TelegramRegisterStats.ToMany.value]

                        if int(status ) not in showed and account['Phone'] not in process:
                            if int(status) == TelegramRegisterStats.FloodWait.value:
                                flood = db.GetFloodWait(account['Phone'])
                                logging.info('Check that account not  floodwait')
                                if flood is not None and len(flood) == 2:
                                    try:
                                        _time = datetime.datetime.strptime(flood[0], '%Y-%m-%d %H:%M:%S.%f')
                                        seconds = flood[1]
                                        seconds_passed = (datetime.datetime.now() - _time ).total_seconds()
                                        if seconds_passed > seconds:
                                            stoped_accounts.append(account['Phone'])                                       
                                    except ValueError:
                                        stoped_accounts.append(account['Phone'])


                            else:
                                stoped_accounts.append(account['Phone'])
                
                    if len(stoped_accounts)>0:
                        logging.info('Create new account')
                        opened_account = 0 # وقتی در اولین شروع هیچ اکانتی لود نشده با این حلفه به اندازه محدوده اکانتها اگر اکانتی وجود داشته باشد لود میشود
                        while len(process) + opened_account < limit_account and len(stoped_accounts) > 0:
                            random_selected_account = random.choice(stoped_accounts)
                            stoped_accounts.remove(random_selected_account)
                            ps.start(['python', 'join.py', '--account', random_selected_account, '--log', 'debug', '-v'])
                            opened_account +=1
                            sleep(1)
                    else:
                        logging.info('Try to create new account...')
                        count_of_signup_process = len(GetSignUpProcess())
                        if count_of_signup_process == 0 and CheckLimitation():
                            logging.info('No limitation for create account')
                            accounts = db.GetAccounts()
                            try:
                                if accounts is not None or len(accounts) > 0:
                                    last_account =accounts[-1]
                                    _time = last_account[6]
                                    _time = datetime.datetime.strptime(_time, '%Y-%m-%d %H:%M:%S.%f')
                                    logging.info('Last account creation time is %s', _time)
                                    mins = (datetime.datetime.now() - _time).total_seconds() / 60.0 # Create new account each 10 miniuts
                                    logging.info('Last account acreate at %s minutes ago', mins)
                                    if mins >= random.randint(10,20):
                                        ps.start(['python', 'telegram_signup.py', '--log' ,'debug', '-v'])
                            except Exception as e:
                                logging.info(type(e).__name__)
                        else:
                            logging.info('please wait 10 min before two account create')
                else :
                    logging.info('Try to create account...')
                    accounts = db.GetAccounts()
                    mins = 0
                    if accounts is not None or len(accounts) > 0:
                        logging.info('Check last account creation time...')
                        last_account = accounts[-1]
                        _time = last_account[6]
                        _time = datetime.datetime.strptime(_time, '%Y-%m-%d %H:%M:%S.%f')
                        mins = (datetime.datetime.now() - _time).total_seconds() / 60.0 # Create new account each 10 miniuts

                    if CheckLimitation() and len(GetSignUpProcess()) == 0 and (mins >= random.randint(10,20) or mins == 0):
                        ps.start(['python', 'telegram_signup.py', '--log' ,'debug', '-v'])                              

            except KeyboardInterrupt: # fix issue 19
                continue
            except AttributeError: # Fix issue 20
                continue
            except Exception as e:
                logging.info(str(e))

            db.Close()
        sleep(3)

def handler(signum, frame):
    print("ctrl+c")

if __name__ == '__main__' :
    try:
        LogInit('Auto.py')
        signal.signal(signal.SIGINT, handler)  # prevent "crashing" with ctrl+C https://stackoverflow.com/a/59003480/9850815
        main()
    except Exception as e:
        logging.info(str(e))