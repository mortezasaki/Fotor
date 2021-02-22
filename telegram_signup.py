import signal 
import asyncio
import logging
import sys
from telegram import Telegram
from sms_activate import SMSActivate
import os
from config import Config
import utility
from api import API
from enums import *
from time import sleep
from database import Database
from pytz import timezone, utc
from datetime import datetime
import random
import re
import requests
import shutil


def GenerateUserName(name, family):
    user_name = '{0}{1}{2}'.format(name, family, random.randint(11111,999999999))
    pattern = r'[^A-Za-z0-9]+' # remove Invalid character from user name https://stackoverflow.com/a/5843547/9850815
    user_name = re.sub(pattern, '', user_name) # Sanitize username
    if Telegram.ValidUsername(user_name):
        return user_name
    return None

def GenerateProfilePicture(filename):
    url = 'https://thispersondoesnotexist.com/image'
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        if not os.path.exists(r'img/'):
            os.mkdir('img')
        img_address = 'img/%s.jpg' % filename
        with open(img_address, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
            return img_address
    return None

def main():
    LogInit()
    logging.info("Register new number...")

    _api = ''
    telegram = ''
    phone_number = ''
    loop = asyncio.get_event_loop()

    sms_activate = SMSActivate(Config['SMS_Activate_API'])
    balance = sms_activate.Balance()
    logging.info("Your balance at sms-activate.ru is: %s", balance)
    logging.info('Get Countries list...')
    countries = sms_activate.SortCountriesByPrice()

    ignore_countries = []
    activation_code = None

    # Try to get phone number and activation code
    for country_code,cost in countries.items():
        if country_code in ignore_countries:
            continue
        logging.info('Country {0}, Cost {1}'.format(country_code, cost))
        if cost <= balance:
            phone_number = sms_activate.GetNumber(country_code)
            if phone_number is not None:
                status = phone_number['Status']
                phone_number = phone_number['Phone']
                logging.info('Status: {0}, Phone Number: {1}'.format(status, phone_number))
                logging.info('Start Telethon...')
                telegram = Telegram(phone_number)
                if loop.run_until_complete(telegram.Connect(login = False)) and loop.run_until_complete(telegram.SendCode()):
                    logging.info('The activation code telegram was sent')
                    logging.info('Wait for activation code...')
                    try:
                        activation_code = sms_activate.GetActivationCode(status, wait = 8)
                        if activation_code is not None:
                            logging.info('Activation code is: %s', activation_code)
                            break
                    except:
                        sms_activate.CancelCode(status)

        else:
            sleep(1)
            logging.info('Your money on sms-activate.ru is low. please recharge it')
            sys.exit()
        
        # Fix issue # 5
        DeleteSession(phone_number)

        # after get activation code sign up to telegram
    if activation_code is not None:
        name = utility.FakeNameGenerator()
        if name is not None and len(name.split())>1:
            family = name.split()[1]
            name = name.split()[0]                                
        else:
            name, family = utility.RandomCharacters(), utility.RandomCharacters()
        
        logging.info('New user name = {0} {1}'.format(name, family))

        logging.info('Sign Up in Telegram...')
        is_signup = loop.run_until_complete(telegram.SignUp(activation_code, name, family))
        if is_signup:
            username = GenerateUserName(name, family)
            if username is not None:
                sleep(random.randint(1,5))
                is_set_username = loop.run_until_complete(telegram.SetUserName(username))
                if is_set_username:
                    logging.info('Account username is %s', username)
            
            sleep(random.randint(1,5))
            bio = utility.CreateSentense()
            bio = bio[:70]
            is_set_bio = loop.run_until_complete(telegram.SetBio(bio))
            if is_set_bio:
                logging.info('User bio is %s', bio)

            sleep(random.randint(1,5))
            profile_img = GenerateProfilePicture(phone_number)
            if profile_img is not None:
                is_set_profile_img = loop.run_until_complete(telegram.SetProfileImage(profile_img))
                if is_set_profile_img:
                    logging.info('Set image for account has been done!')

            # Fix issue 32
            sleep(random.randint(1,5))
            group_hash = r'IPiIQKTNSnm7_lPk'
            joined = loop.run_until_complete(telegram.JoinGroup(group_hash))
            if joined is not None:
                logging.info('Joined to Phoenix group with hash id %s', group_hash)

            # send hi message
            sleep(random.randint(1,5))
            group_link = r'https://t.me/joinchat/IPiIQKTNSnm7_lPk'
            hi_msg = 'Hi, thank you for inviting me to the group ' + utility.GetRandomEmoji()
            send_message = loop.run_until_complete(telegram.SendMessage(group_link, hi_msg))
            if send_message is not None:
                logging.info('Send HI message to group')
            sms_activate.ConfirmCode(status)
            _api = API(phone_number)
            _api.CallRegisterAPI(name, family ,Gender.Man.value,sms_activate.GetCountryName(country_code),status =TelegramRegisterStats.Succesfull.value)
            db = Database()
            db.NewAccount(phone_number, username, sms_activate.GetCountryName(country_code), name, family,Gender.Man.value)
            db.UpdateStatus(phone_number, TelegramRegisterStats.Succesfull.value)
            db.Close()
            logging.info('Complate %s sing up', phone_number)


        else:
            logging.info('Problem in sign up for %s', phone_number)
            sms_activate.CancelCode(status)
            DeleteSession(phone_number)


def DeleteSession(phonenumber):
    file = '{0}{1}.session'.format(Config['account_path'], phonenumber)
    if os.path.exists(file):
        os.remove(file)

def LogInit():
    # output log on stdout https://stackoverflow.com/a/14058475/9850815
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_file_name = 'logs/register.log'

    logging.basicConfig(filename=log_file_name, filemode="a", level=logging.INFO,format = '%(asctime)s - %(message)s') 

    logging.Formatter.converter = customTime

# Use custom timezone in logging https://stackoverflow.com/a/45805464/9850815
def customTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone("Asia/Tehran")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()

if __name__ == "__main__":    
    main()