import os
from config import Config
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import errors
import asyncio
import utility
import logging
import socks
import re
from time import sleep
from enums import *
from database import Database

class Telegram:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        if not os.path.exists(Config['account_path']):
            os.makedirs(Config['account_path'])

        self.tg_client = ''

    def ValidUsername(self, username : str):
        pattern = r'^[a-zA-Z]\w{5,}$'
        if re.match(pattern, username):
            return True
        return False
    

    async def SendCode(self):
        try:
            await self.tg_client.send_code_request(self.phone_number)
            return True
        except:
            return False

    async def SignUp(self, activation_code, name, family):
        try:
            await self.tg_client.sign_up(activation_code, name, family)
            return True
        except:
            return False

    async def Connect(self, use_proxy = False):
        tg_session_location = '{0}{1}.session'.format(Config['account_path'],self.phone_number)

        if use_proxy:
            proxies = utility.GetProxy()
            if proxies is not None:
                for proxy in proxies:
                    try:
                        # Set proxy for telethon https://github.com/LonamiWebs/Telethon/issues/227
                        host = proxy['IP']  # a valid host
                        port = int(proxy['Port'])  # a valid port
                        logging.info('Proxy address is {0}:{1} from {2}'.format(host,port,proxy['Country']))
                        proxy = (socks.HTTP, host, port)

                        self.tg_client = TelegramClient(tg_session_location, Config['tg_api_id'], Config['tg_api_hash'],
                            device_model = 'Galaxy J5 Prime' , system_version = 'SM-G570F', app_version = '1.0.1',
                            flood_sleep_threshold = Config['flood_sleep_threshold'], proxy=proxy)
                        
                        await self.tg_client.connect()
                        return True
                        break
                    except Exception as e:
                        logging.info(str(e))
                        await self.tg_client.disconnect()
                        # await self.tg_client.log_out()
                        logging.info("Proxy not working")
                        continue
        
        else:
            self.tg_client = TelegramClient(tg_session_location, Config['tg_api_id'], Config['tg_api_hash'],
                device_model = 'Galaxy J5 Prime' , system_version = 'SM-G570F', app_version = '1.0.1')  
        
        await self.tg_client.connect()
        if self.tg_client.is_connected() :
            return True
        return False

    async def Search(self, username : str):
        if self.ValidUsername(username):
            try :
                return await self.tg_client.get_entity(username)
            except ValueError: 
                logging.info('Value Error accured')                 
                return None
            except errors.FloodWaitError as e:
                logging.info('Flood wait for %s' % e.seconds)
                logging.info('Disconnect...')
                db = Database()
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
                db.Close()
                await self.tg_client.disconnect()
                sleep(e.seconds)
                logging.info('Connect and login...')
                await self.Connect()
            except errors.UserDeactivatedBanError:
                logging.info('The user has been banned')
                AddToBan(phone_number)
                exit()
            except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
                logging.info('Account has auth problem')
                AddToAuthKeyUnregisteredError(phone_number)
                exit()

            except errors.SessionPasswordNeededError: # TODO: Handle when account has password
                logging.info('Account has password')
                exit()

            except Exception as e:
                print(type(e).__name__)
                logging.info(str(e))
                await self.Connect()                 
        return None

    async def JoinChannel(self, username : str):
        if await self.Search(username):
            try :
                return await self.tg_client(JoinChannelRequest(username))
            except ValueError: 
                logging.info('Value Error accured')                 
                return None
            except errors.FloodWaitError as e:
                logging.info('Flood wait for %s' % e.seconds)
                logging.info('Disconnect...')
                db = Database()
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
                db.Close()
                await self.tg_client.disconnect()
                sleep(e.seconds)
                logging.info('Connect and login...')
                await self.Connect()
            except errors.UserDeactivatedBanError:
                logging.info('The user has been banned')
                AddToBan(phone_number)
                exit()
            except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
                logging.info('Account has auth problem')
                AddToAuthKeyUnregisteredError(phone_number)
                exit()

            except errors.SessionPasswordNeededError: # TODO: Handle when account has password
                logging.info('Account has password')
                exit()

            except Exception as e:
                print(type(e).__name__)
                logging.info(str(e))
                await self.Connect()                
        return None

    async def GetChannels(self):
        channels=[]
        async for dialog in self.tg_client.iter_dialogs():
            if not dialog.is_group and dialog.is_channel:
                channels.append(dialog)
        print(channels)
        return channels


def AddToBan(account : str):
    with open('ban.txt','a') as f:
        f.write('%s\n' % account)

def AddToAuthKeyUnregisteredError(account : str):
    with open('autherror.txt','a') as f:
        f.write('%s\n' % account)