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
        self.tg_session_location = '{0}{1}.session'.format(Config['account_path'],self.phone_number)


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

                        self.tg_client = TelegramClient(self.tg_session_location, Config['tg_api_id'], Config['tg_api_hash'],
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
            self.tg_client = TelegramClient(self.tg_session_location, Config['tg_api_id'], Config['tg_api_hash'],
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
                return None
            except errors.FloodWaitError as e:
                logging.info('Flood wait for %s' % e.seconds)
                logging.info('Disconnect...')
                await self.tg_client.disconnect()
                sleep(e.seconds)
                logging.info('Connect and login...')
                await self.Login()                
        return None

    async def JoinChannel(self, username : str):
        if await self.Search(username):
            try :
                return await self.tg_client(JoinChannelRequest(username))
            except ValueError:  
                return None
            except errors.FloodWaitError as e:
                logging.info('Flood wait for %s' % e.seconds)
                logging.info('Disconnect...')
                await self.tg_client.disconnect()
                sleep(e.seconds)
                logging.info('Connect and login...')
                await self.Login()
        return None

    async def GetChannels(self):
        channels=[]
        async for dialog in self.tg_client.iter_dialogs():
            if not dialog.is_group and dialog.is_channel:
                channels.append(dialog)
        print(channels)
        return channels