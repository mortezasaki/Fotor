# Programming by Morteza Saki 26 Jan 2021

# Fix SyntaxError: Non-ASCII character https://stackoverflow.com/a/10589674/9850815
# -*- coding: utf-8 -*-

"""
از این کلاس برای جوین اتوماتیک در تلگرام استفاده میشود. ورودی این برنامه شماره تلفنی است که قبلا ثبت نام و لاگین شده است.
با دریافت این شماره تلفن به دنبال یک سشن تلگرام میگردد و بعد از پیدا کردن آن وارد تلگرام میشود و شروع به جوین شدن میکند
"""

import sys
import utility 
from config import Config
import os
import asyncio
import logging
from time import sleep
from api import API
from enums import *
import getopt
import signal
from telegram import Telegram
from sms_activate import SMSActivate


loop = asyncio.get_event_loop()

def LogInit():
    # output log on stdout https://stackoverflow.com/a/14058475/9850815
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_file_name = 'logs/%s.log' % os.getpid()

    logging.basicConfig(filename=log_file_name, filemode="w", level=logging.INFO,format = '%(asctime)s - %(message)s') 

    
def ExistAccount(account : str):
    account_location = "%s%s.session" % (Config['account_path'],account)
    if os.path.exists(account_location):
        return True
    return False

def AccountIsBanned(account : str):
    if os.path.exists('ban.txt'):
        with open('ban.txt','r') as f:
            accounts = f.readlines()
            for _account in accounts:
                if account == _account.replace('\n',''):
                    return True
    return False

def AccountHasAuthProblem(account : str):
    if os.path.exists('autherror.txt'):
        with open('autherror.txt','r') as f:
            accounts = f.readlines()
            for _account in accounts:
                if account == _account.replace('\n',''):
                    return True
        return False    

def main():
    signal.signal(signal.SIGINT, handler)  # prevent "crashing" with ctrl+C https://stackoverflow.com/a/59003480/9850815
    LogInit()
    argv = sys.argv[1:] 

    login = False
    _api = ''
    telegram = ''
    phone_number = ''
    try: 
        opts, args = getopt.getopt(argv, shortopts='a:l:v', longopts = ["account=", "log=", "verbose"]) 
        for opt, arg in opts: 
            logging.info(opt)
            if opt in ['-a', '--account']: 
                phone_number = arg
                if ExistAccount(phone_number) and (not AccountIsBanned(phone_number) and not AccountHasAuthProblem(phone_number)):
                    logging.info('Start login to %s' % phone_number)
                    login = True
                    break
                else :
                    logging.info('Account has problem or maybe it banned or not exist')
                    exit(1)
    except SystemExit:
        logging.info('Account has problem or maybe it banned or not exist')
        exit()
    
    except Exception as e:
        logging.info(str(e))
        logging.info(type(e).__name__)
        exit()


    telegram = Telegram(phone_number)
    _api = API(phone_number)
    _api.CallRegisterAPI("test", "test" ,Gender.Man.value,'Russia',status =TelegramRegisterStats.Succesfull.value) # Todo: create a api to check number exist in db
    
    while True:
        channel = _api.CallGetChannel()
        if channel is not None:
            channel_username = channel['username']
            logging.info('Joining to %s channel' % channel_username)
            channel_id = channel['_id']
            try:
                loop.run_until_complete(telegram.Search(channel_username))
                loop.run_until_complete(telegram.JoinChannel(channel_username))
                if _api.CallJoin(channel_id):
                    logging.info('Join was done')
                sleep(1)
            except Exception as e:
                print(type(e).__name__)
                logging.info(str(e))


def handler(signum, frame):
    print("ctrl+c")

if __name__ == "__main__":
    main()
