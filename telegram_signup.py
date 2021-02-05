import asyncio
import logging
import signal
from telegram import Telegram
from sms_activate import SMSActivate
import os
from config import Config
import utility
from api import API
from enums import *
from time import sleep
from database import Database


def main():
    signal.signal(signal.SIGINT, handler)  # prevent "crashing" with ctrl+C https://stackoverflow.com/a/59003480/9850815
    LogInit()
    logging.info("Register new number...")

    _api = ''
    telegram = ''
    phone_number = ''
    loop = asyncio.get_event_loop()

    sms_activate = SMSActivate(Config['SMS_Activate_API'])
    balance = sms_activate.Balance()
    logging.info("Your balance at sms-activate.ru is: %s" % balance)
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
                if loop.run_until_complete(telegram.Connect()) and loop.run_until_complete(telegram.SendCode()):
                    logging.info('The activation code telegram was sent')
                    logging.info('Wait for activation code...')
                    try:
                        activation_code = sms_activate.GetActivationCode(status)
                        if activation_code is not None:
                            logging.info('Activation code is: %s' % activation_code)
                            break
                        sms_activate.CancelCode(status)
                    except:
                        sms_activate.CancelCode(status)

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
            sms_activate.ConfirmCode(status)
            _api = API(phone_number)
            _api.CallRegisterAPI(name, family ,Gender.Man.value,sms_activate.GetCountryName(country_code),status =TelegramRegisterStats.Succesfull.value)
            db = Database()
            db.NewAccount(phone_number, sms_activate.GetCountryName(country_code), name, family,0)
            logging.info('Complate %s sing up' % phone_number)

def LogInit():
    # output log on stdout https://stackoverflow.com/a/14058475/9850815
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_file_name = 'logs/%s.log' % os.getpid()

    logging.basicConfig(filename=log_file_name, filemode="w", level=logging.INFO,format = '%(asctime)s - %(message)s') 


def handler(signum, frame):
    print("ctrl+c")

if __name__ == "__main__":
    main()