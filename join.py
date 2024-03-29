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

def CheckVPN(retry = 60, wait = 10):
    logging.info('Check VPN...')
    get_vpn_retry = retry
    while get_vpn_retry > 0:
        try:
            req = requests.get('https://ifconfig.me')
            if req.status_code == 200:
                ip = req.text
                if ip == Config['server_ip']: # VPN not connected
                    logging.info('Problem connecting to the VPN')
                    sleep(wait)
                else:
                    logging.info('VPN is OK!')
                    return True
        except Exception as e:
            logging.info(type(e).__name__)
        get_vpn_retry-=1
    return False

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
    if not CheckVPN():
        logging.info('Fail to connect VPN. Exit...')
        sys.exit()
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
            5, # Forward channel post message
        ]
        while True:
            db = Database()
            db.UpdateStatus(phone_number, TelegramRegisterStats.Running.value)
            emoji = utility.GetRandomEmoji()
            do_action = random.choice(action, weights=(50, 10, 10, 10, 10, 10), k=6)
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
                            if not CheckVPN():
                                logging.info('Fail to connect VPN. Exit...')
                                sys.exit()
                            joined = loop.run_until_complete(telegram.JoinChannel(channel_username))
                            if joined is not None:
                                db.Join(phone_number, channel_username)
                                if _api.CallJoin(channel_id):
                                    logging.info('Joining the channel has been successful.')
                                    logging.info('The view increase...')
                                    view = loop.run_until_complete(telegram.IncreasingView(channel_username))                        
                                    if view:
                                        logging.info('The view increase was successful')
                                    else:
                                        logging.info('Problem with increasing views')
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
                if not CheckVPN():
                    logging.info('Fail to connect VPN. Exit...')
                    sys.exit()
                loop.run_until_complete(telegram.SendMessage(group_link, emoji))
            elif do_action == 2: # Send Gif
                logging.info('Sending gif to Phoenix group...')
                gif = utility.DownloadGif()
                if gif is not None:
                    if not CheckVPN():
                        logging.info('Fail to connect VPN. Exit...')
                        sys.exit()
                    loop.run_until_complete(telegram.SendFile(group_link, gif))    
            elif do_action == 3: # Send random sentense
                sentense = utility.CreateSentense()
                if not CheckVPN():
                    logging.info('Fail to connect VPN. Exit...')
                    sys.exit()
                send_message = loop.run_until_complete(telegram.SendMessage(group_link, sentense))
                if send_message is not None:
                    logging.info('Sending message to group')   
            elif do_action == 4: # Mention a user
                if not CheckVPN():
                    logging.info('Fail to connect VPN. Exit...')
                    sys.exit()
                messages = loop.run_until_complete(telegram.GetMessage(group_link))
                if messages is not None:
                    random_message = random.choice(messages)
                    user_name = random_message.sender.username
                    if user_name is not None:
                        msg = r'@' + user_name
                        if not CheckVPN():
                            logging.info('Fail to connect VPN. Exit...')
                            sys.exit()
                        mention_user = loop.run_until_complete(telegram.SendMessage(group_link, msg))
                        if mention_user is not None:
                                logging.info('Mentioned %s', user_name)
            elif do_action == 5: # Forward message
                famous_channels = ['varzesh3','gizmiztel','AKHARINKHABAR','PERSPOLIS','KHOOROOSJANGI','nagahan_com','ESTEGHLALPAGE',
                                    'niazcom_ir', 'parsinehnews','tgacademy', 'Tebe_slami_irani', 'Dr_SalamatX', 'TVnavad', 'Ravan6enasii',
                                    'khandehabadd', 'serfan_jahate_ettela', 'NiazCom', 'bahseazad']
                channel = random.choice(famous_channels)
                if not CheckVPN():
                    logging.info('Fail to connect VPN. Exit...')
                    sys.exit()
                messages = loop.run_until_complete(telegram.GetMessage(channel))
                if messages is not None:
                    msg = random.choice(messages)
                    if not CheckVPN():
                        logging.info('Fail to connect VPN. Exit...')
                        sys.exit()
                    send_forward_message = loop.run_until_complete(telegram.ForwardMessage(group_link, msg))
                    if send_forward_message is not None:
                        logging.info('Forward a message from %s to Phoenix group', channel)
            elif do_action == 6:
                logging.info('Increasing view...')
                res = loop.run_until_complete(telegram.IncreasingView())                        
                if res:
                    logging.info('Successful increasing view')
                else:
                    logging.info('Fail increasing view')
            db.Close()
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
