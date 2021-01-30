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
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import errors
import os
import asyncio
import re
import logging
from time import sleep
from api import API
from enums import *
import requests
import socks


logging.getLogger().setLevel(logging.INFO)

class SMSActivate:
    def __init__(self, api_key : str):
        self.api_key = api_key
        
    def Balance(self):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key=%s&action=getBalance' % self.api_key
        req = requests.get(url)

        if req.status_code == 200: 
            res = req.text
            pattern = r'^(ACCESS_BALANCE:)\d+(\.\d+)?$'
            if re.match(pattern, res): # Example ACCESS_BALANCE:389.98%
                try:
                    balance = float(res.split(':')[1])
                    return balance
                except:
                    logging.info("Can't extract balance")
        
        return False

    def GetCountry(self):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key=%s&action=getCountries' % self.api_key
        req = requests.get(url)

        if req.status_code == 200:
            try: 
                res = req.json()
                countries = {}
                for _id,names in res.items():
                    countries[_id] =  names['eng']
                return countries
            except:
                return None
        else:
            return None

    def GetPrice(self, country_code, service : str = 'tg'):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key={0}&action=getPrices&service={1}&country={2}'.format(self.api_key, service, country_code)
        req = requests.get(url)        

        if req.status_code == 200:
            try:
                res = req.json()
                return res[str(country_code)][service]['cost']
            except:
                return None
        return None

    def SortCountriesByPrice(self):
        countries = self.GetCountry()

        if countries is not None:
            costs = {}

            for country in countries.keys():
                price = self.GetPrice(country)
                if price is not None:
                    costs[country] = price
            sorted_costs = utility.SortDic(costs)
            return sorted_costs
        return None

    def GetNumber(self, country_code, service= 'tg', retry : int = 5, wait : float = 3):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key={0}&action=getNumber&service={1}&country={2}'.format(self.api_key, service, country_code)
        for i in range(retry):
            req = requests.get(url)        

            if req.status_code == 200:
                try:
                    response = req.text
                    pattern = r'^(ACCESS_NUMBER:)\d{8,}(:)\d{8,}$'
                    if re.match(pattern, response):
                        status_code = response.split(':')[1]
                        phone_number = response.split(':')[2]
                        return {'Status' : status_code, 'Phone' : phone_number}
                except:
                    return None
            sleep(wait)
        return None

    def ChangeNumberStatus(self,id, status):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key={0}&action=setStatus&status={1}&id={2}'.format(self.api_key, status, id)
        req = requests.get(url)        

        if req.status_code == 200:
            return req.text
        return None

    def ConfirmCode(self, id):
        result = self.ChangeNumberStatus(id, SMSActivateSMSStatus.Complate.value)
        if result is not None and result == 'ACCESS_ACTIVATION':
            return True
        return False
    
    def CancelCode(self, id):
        result = self.ChangeNumberStatus(id, SMSActivateSMSStatus.Cancel.value)
        if result is not None and result == 'ACCESS_CANCEL':
            return True
        return False

    def GetActivationCode(self, id, *, retry : int = 10, wait : float = 5):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key={0}&action=getStatus&id={1}'.format(self.api_key, id)
        for i in range(retry):
            req = requests.get(url)        

            if req.status_code == 200:
                pattern = r'^(STATUS_OK:)\d{5}$' # ex STATUS_OK:20980
                if re.match(pattern, req.text):
                    return req.text.split(':')[1]
            sleep(wait)
        return None 

class Telegram:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        if not os.path.exists(Config['account_path']):
            os.makedirs(Config['account_path'])

        android_model = utility.AndroidDeviceGenerator()
        android_model = android_model if android_model is not None else Config['android_model']

        self.tg_session_location = '{0}{1}.session'.format(Config['account_path'],self.phone_number)

        proxy = utility.GetProxy()
        if proxy is not None:
            # Set proxy for telethon https://github.com/LonamiWebs/Telethon/issues/227
            host = proxy['IP']  # a valid host
            port = int(proxy['Port'])  # a valid port
            proxy = (socks.SOCKS4, host, port)

            self.tg_client = TelegramClient(self.tg_session_location, Config['tg_api_id'], Config['tg_api_hash'],
                device_model = 'Galaxy J5 Prime' , system_version = 'SM-G570F', app_version = '1.0.1',
                flood_sleep_threshold = Config['flood_sleep_threshold'], proxy=proxy)
        else:
            self.tg_client = TelegramClient(self.tg_session_location, Config['tg_api_id'], Config['tg_api_hash'],
                device_model = 'Galaxy J5 Prime' , system_version = 'SM-G570F', app_version = '1.0.1',
                flood_sleep_threshold = Config['flood_sleep_threshold'])            

    def ValidUsername(self, username : str):
        pattern = r'^[a-zA-Z]\w{5,}$'
        if re.match(pattern, username):
            return True
        return False
    

    async def SendCode(self):
        await self.tg_client.connect()
        
        await self.tg_client.connect()
        if self.tg_client.is_connected():
            try:
                await self.tg_client.send_code_request(self.phone_number)
                return True
            except:
                return False
        return False

    async def SignUp(self, activation_code, name, family):
        try:
            await self.tg_client.sign_up(activation_code, name, family)
            return True
        except:
            return False

    async def Login(self):
        pass
        # tg_session_location = '{0}{1}.session'.format(Config['account_path'],self.phone_number)
        # if os.path.exists(tg_session_location):
        #     self.client = TelegramClient(tg_session_location, Config['tg_api_id'], Config['tg_api_hash'],
        #         device_model = ConfSMS_Activate_APIig['device_model'], system_version = Config['system_version'], app_version = Config['app_version'],
        #         flood_sleep_threshold = Config['flood_sleep_threshold'])
        #     await self.client.connect()
        #     if self.client.is_connected():
        #         return True
        #     return False
        # else:
        #     raise False

    async def Search(self, username : str):
        if self.ValidUsername(username):
            try :
                return await self.tg_client.get_entity(username)
            except ValueError:
                return None
            except errors.FloodWaitError as e:
                logging.info('Flood wait for %s' % e.seconds)
                sleep(e.seconds)
        return None

    async def JoinChannel(self, username : str):
        if self.Search(username):
            try :
                return await self.tg_client(JoinChannelRequest(username))
            except ValueError:  
                return None
            except errors.FloodWaitError as e:
                logging.info('Flood wait for %s' % e.seconds)
                sleep(e.seconds)
        return None

    async def GetChannels(self):
        channels=[]
        async for dialog in self.tg_client.iter_dialogs():
            if not dialog.is_group and dialog.is_channel:
                channels.append(dialog)
        print(channels)
        return channels


if __name__ == "__main__":
    logging.info("Start Fotor...")

    loop = asyncio.get_event_loop()

    sms_activate = SMSActivate(Config['SMS_Activate_API'])
    _api = ''
    telegram = ''
    balance = sms_activate.Balance()
    logging.info("Your balance at sms-activate.rus is: %s" % balance)
    countries = sms_activate.SortCountriesByPrice()

    is_signup = False
    ignore_countries = ['6']

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
                connect_to_telegram = loop.run_until_complete(telegram.SendCode())
                if connect_to_telegram:
                    logging.info('The activation code telegram was sent')
                    logging.info('Wait for activation code...')
                    try:
                        activation_code = sms_activate.GetActivationCode(status)
                        if activation_code is not None:
                            logging.info('Activation code is: %s' % activation_code)                    
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
                                _api.CallRegisterAPI(name, family ,Gender.Man.value,'Russia',status =TelegramRegisterStats.Succesfull.value)
                                logging.info('Complate %s sing up' % phone_number)
                                break
                    except:
                        sms_activate.CancelCode(status)


    if is_signup:
        logging.info('Start joining...')
        
        while True:
            channel = _api.CallGetChannel()
            if channel is not None:
                channel_username = channel['username']
                logging.info('Join to %s' % channel_username)
                channel_id = channel['_id']
                try:
                    loop.run_until_complete(telegram.Search(channel_username))
                    loop.run_until_complete(telegram.JoinChannel(channel_username))
                    if _api.CallJoin(channel_id):
                        logging.info('Join was doned')
                    sleep(1)
                except errors.UserDeactivatedBanError:
                    logging.info('The user has been banned')
                    exit()
                except Exception as e:
                    logging.info(str(e)) 


