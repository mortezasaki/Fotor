# For Issue 7

import psutil, re, os
from config import Config
from enums import *
from database import Database
import utility, ps
import random
from time import sleep
import datetime

def GetPhoneFromCMDLine(cmdline):
    pattern = r'\d{10,}'
    match = re.search(pattern, cmdline)
    if match:
        return match[0]
    else:
        return None

def GetJoinProcess():
    process = []
    for p in psutil.process_iter():
        try:
            cmdline = ' '.join(p.cmdline())
            pattern = r'\d{10,}'
            if 'join.py' in cmdline and re.search(pattern, cmdline):
                phone_number = GetPhoneFromCMDLine(cmdline)
                process.append(phone_number)
        except psutil.NoSuchProcess:
            continue
    
    return process

def GetSignUpProcess():
    process = []
    for p in psutil.process_iter():
        try:
            cmdline = ' '.join(p.cmdline())
            pattern = r'\d{10,}'
            if 'telegram_signup.py' in cmdline:
                process.append(p)
        except psutil.NoSuchProcess:
            continue
    
    return process    

def main():
    limit_account = Config['limit_account']
    while True:
        process = GetJoinProcess()
        if len(process) < limit_account:
            accounts = []
            db = Database()
            try:
                for file in os.listdir(Config['account_path']):
                    if file.endswith(".session"):
                        phone_number = file.split('.')[0]
                        if utility.ValidatePhone(phone_number):
                            status = db.GetStatus(phone_number)
                            accounts.append({'Phone' : phone_number, 'Status' : status})
                
                stoped_accounts = []
                
                if accounts is not None:
                    for account in accounts:
                        status = account['Status']
                        showed = [TelegramRegisterStats.Ban.value, TelegramRegisterStats.AuthProblem.value, TelegramRegisterStats.HasPassword.value]

                        if int(status ) not in showed and account['Phone'] not in process:
                            if int(status) == TelegramRegisterStats.FloodWait.value:
                                flood = db.GetFloodWait(account['Phone'])
                                if len(flood) == 2:
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
                        opened_account = 0 # وقتی در اولین شروع هیچ اکانتی لود نشده با این حلفه به اندازه محدوده اکانتها اگر اکانتی وجود داشته باشد لود میشود
                        while len(process) + opened_account < limit_account and len(stoped_accounts) > 0:
                            random_selected_account = random.choice(stoped_accounts)
                            stoped_accounts.remove(random_selected_account)
                            ps.start(['python', 'join.py', '--account', random_selected_account, '--log', 'debug', '-v'])
                            opened_account +=1
                            sleep(1)
                    else:
                        count_of_signup_process = len(GetSignUpProcess())
                        if (len(stoped_accounts) + count_of_signup_process) < limit_account:
                            ps.start(['python', 'telegram_signup.py', '--log' ,'debug', '-v'])
                else :
                    ps.start(['python', 'telegram_signup.py', '--log' ,'debug', '-v'])
            except FileNotFoundError:
                print('No such file or directory')

            db.Close()



if __name__ == '__main__' :
    main()