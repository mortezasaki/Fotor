# Programming by Morteza Saki 26 Jan 2021

# Fix SyntaxError: Non-ASCII character https://stackoverflow.com/a/10589674/9850815
# -*- coding: utf-8 -*-

"""
از این کلاس برای جوین اتوماتیک در تلگرام استفاده میشود. ورودی این برنامه شماره تلفنی است که قبلا ثبت نام و لاگین شده است.
با دریافت این شماره تلفن به دنبال یک سشن تلگرام میگردد و بعد از پیدا کردن آن وارد تلگرام میشود و شروع به جوین شدن میکند
"""
import signal 
# Fix issue 22
# احساس میشه وقتی که در منوی لاگ کنترل سی زده میشه اگه در ابتدای این فایل باشه چون به قسمت هندل کردن 
# KeyboardBreak نرسیده خطا میدهد.
# به همین منظور هندل کردن این مورد را در ابتدای فایل می آوریم
def handler(signum, frame):
    print("ctrl+c")
signal.signal(signal.SIGINT, handler)  # prevent "crashing" with ctrl+C https://stackoverflow.com/a/59003480/9850815


import sys
import requests
from config import Config
import os
import asyncio
import logging
from time import sleep
from api import API
from enums import *
import getopt
from telegram import Telegram
from database import Database
from pytz import timezone, utc
from datetime import datetime
import random
import utility

def LogInit(phone_number):
    # output log on stdout https://stackoverflow.com/a/14058475/9850815
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_file_name = 'logs/join.log'

    logging.basicConfig(filename=log_file_name, filemode="a", level=logging.INFO,
        format = '%(asctime)s - {0} - %(message)s'.format(phone_number), datefmt="%Y-%m-%d %H:%M:%S") 
    
    logging.Formatter.converter = customTime

# Use custom timezone in logging https://stackoverflow.com/a/45805464/9850815
def customTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone("Asia/Tehran")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()

def main():
    argv = sys.argv[1:] 
    loop = asyncio.get_event_loop()
    phone_number = ''
    try: 
        opts, args = getopt.getopt(argv, shortopts='a:l:v', longopts = ["account=", "log=", "verbose"]) 
        for opt, arg in opts: 
            if opt in ['-a', '--account']: 
                phone_number = arg
                LogInit(phone_number)
                logging.info('Start login to %s', phone_number)
                login = True
                break
    
    except Exception as e:
        logging.info(str(e))
        logging.info(type(e).__name__)
        sys.exit()

    # Fix #2
    if not ExistAccount(phone_number):
        sleep(1)
        logging.info('%s not exist in accounts directory', phone_number)        
        sys.exit()

    telegram = Telegram(phone_number)
    if loop.run_until_complete(telegram.Connect()):
        _api = API(phone_number)
        _api.CallRegisterAPI("test", "test" ,Gender.Man.value,'Russia',status =TelegramRegisterStats.Succesfull.value) # Todo: create a api to check number exist in db

        group_link = r'https://t.me/joinchat/IPiIQKTNSnm7_lPk'

        action = [
            0, # Join channel
            1, # Send emoji
            2, # Send gif
            3, # Send a random sentense
            4, # Mention user
            # 4, # Forward channel post message
            # 5, # Send picture
        ]

        while True:
            emoji = utility.GetRandomEmoji()
            do_action = random.choice(action)
            if do_action == 0: # Join   
                try_to_connect_membersgram = 10
                while try_to_connect_membersgram > 0: # fix Issue 15
                    channel = _api.CallGetChannel()
                    if channel is not None:
                        try_to_connect_membersgram = 10
                        channel_username = channel['username']
                        logging.info('Joining to %s channel', channel_username)
                        channel_id = channel['_id']
                        try:
                            joined = loop.run_until_complete(telegram.JoinChannel(channel_username))
                            if joined is not None:
                                db = Database()
                                db.Join(phone_number, channel_username)
                                db.UpdateStatus(phone_number, TelegramRegisterStats.Running.value)
                                db.Close()
                                if _api.CallJoin(channel_id):
                                    logging.info('Join was done')
                                    break

                        except ConnectionError:
                            logging.info('Connection error')                          
                            break
                        except SystemExit:
                            logging.info('Exit...')
                            sys.exit()
                        except Exception as e:
                            logging.info(type(e).__name__, ' JoinClass')
                            break
                    else:
                        try_to_connect_membersgram = try_to_connect_membersgram - 1
                
                if try_to_connect_membersgram == 0:
                    logging.info("Can't connect to membersgram server and exit")

            elif do_action == 1: # Send Emoji
                logging.info('Sending emoji to Phoenix group...')
                loop.run_until_complete(telegram.SendMessage(group_link, emoji))
            elif do_action == 2: # Send Gif
                logging.info('Sending gif to Phoenix group...')
                gif = utility.DownloadGif()
                if gif is not None:
                    loop.run_until_complete(telegram.SendFile(group_link, gif))    
            elif do_action == 3: # Send random sentense
                sentense = utility.CreateSentense()
                send_message = loop.run_until_complete(telegram.SendMessage(group_link, sentense))
                if send_message is not None:
                    logging.info('Sending message to group')   
            elif do_action == 4: # Mention a user
                messages = loop.run_until_complete(telegram.GetMessage(group_link))
                random_message = random.choice(messages)
                user_name = random_message.sender.username
                msg = r'@' + user_name
                mention_user = loop.run_until_complete(telegram.SendMessage(group_link, msg))
                if mention_user is not None:
                        logging.info('Mentioned %s', user_name) 
            sleep(random.randint(5,15))     

                    
def ExistAccount(phonenumber):
    if not os.path.exists(Config['account_path']):
        return False
    for file in os.listdir(Config['account_path']):
        name = file.split('.')
        if len(name) == 2 and name[0] == phonenumber and name[1] == "session":
            return True
    return False



if __name__ == "__main__":
    main()
