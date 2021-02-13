import os
from config import Config
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import errors, functions
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

    async def Connect(self, use_proxy = False, login = True):
        tg_session_location = '{0}{1}.session'.format(Config['account_path'],self.phone_number)
        if login and not os.path.exists(tg_session_location):
            exit()

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
            try:
                self.tg_client = TelegramClient(tg_session_location, Config['tg_api_id'], Config['tg_api_hash'],
                    device_model = 'Galaxy J5 Prime' , system_version = 'SM-G570F', app_version = '1.0.1')  
            except TypeError:
                os.remove(tg_session_location)                
                exit()
            except SystemExit():
                exit()
        
        try:
            await self.tg_client.connect()
            if self.tg_client.is_connected() :
                return True
        except errors.TimeoutError:
            logging.info('Fail to connect.')
            return False
        except Exception as e:
            logging.info(type(e).__name__)
        return False

    async def Search(self, username : str):
        if self.ValidUsername(username):
            db = Database()
            try :
                return await self.tg_client.get_entity(username)
            except ValueError: 
                logging.info('Value Error accured')                 
                return None
            except errors.FloodWaitError as e:
                logging.info('Flood wait for %s' % e.seconds)
                logging.info('Exit...')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
                db.UpdateFlooWait(self.phone_number, e.seconds)
                await self.tg_client.disconnect()
                exit()
            except errors.UserDeactivatedBanError:
                logging.info('The user has been banned')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
                exit()
            except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
                logging.info('Account has auth problem')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
                exit()
            except errors.SessionPasswordNeededError: # TODO: Handle when account has password
                logging.info('Account has password')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
                exit()
            except errors.ChannelsTooMuchError:
                logging.info('You have joined too many channels/supergroups.')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
                exit()
            except errors.ChannelPrivateError:
                logging.info('The channel specified is private and you lack permission to access it. Another reason may be that you were banned from it.')
                return None
            except errors.RPCError: # from https://github.com/LonamiWebs/Telethon/issues/1428 for issue 12
                pass                  
            except errors.ChannelBannedError:
                logging.info('The channel is banned')
                return None
            except errors.ChannelInvalidError:
                logging.info('The channel has invalid error')
                return None                
            except Exception as e:
                print(type(e).__name__)
                logging.info(str(e))
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.Stop.value)
                exit()              
            finally:
                db.Close()                                
        return None

    async def JoinChannel(self, username : str):
        if await self.Resolve(username):
            db = Database()
            try :
                return await self.tg_client(JoinChannelRequest(username))
            except ValueError: 
                logging.info('Value Error accured')                 
                return None
            except errors.FloodWaitError as e:
                logging.info('Flood wait for %s' % e.seconds)
                logging.info('Exit...')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
                db.UpdateFlooWait(self.phone_number, e.seconds)
                await self.tg_client.disconnect()
                exit()
            except errors.UserDeactivatedBanError:
                logging.info('The user has been banned')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
                exit()
            except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
                logging.info('Account has auth problem')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
                os.remove('{0}{1}.session'.format(Config['account_path'], self.phone_number))
                exit()

            except errors.SessionPasswordNeededError: # TODO: Handle when account has password
                logging.info('Account has password')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
                exit()
            except errors.ChannelsTooMuchError:
                logging.info('You have joined too many channels/supergroups.')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
                exit()
            except errors.ChannelPrivateError:
                logging.info('The channel specified is private and you lack permission to access it. Another reason may be that you were banned from it.')
                return None
            except errors.RPCError: # from https://github.com/LonamiWebs/Telethon/issues/1428 for issue 12
                pass
            except errors.ChannelBannedError:
                logging.info('The channel is banned')
                return None
            except errors.ChannelInvalidError:
                logging.info('The channel has invalid error')
                return None                          
            except Exception as e:
                logging.info(type(e).__name__)
                logging.info(str(e))
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.Stop.value)
                exit()
            finally:
                db.Close()               
        return None

    async def Resolve(self, username : str):
        db = Database()
        try:
            return await self.tg_client(functions.contacts.ResolveUsernameRequest(username))
        except errors.FloodWaitError as e:
            logging.info('Flood wait for %s' % e.seconds)
            logging.info('Exit...')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
            db.UpdateFlooWait(self.phone_number, e.seconds)
            await self.tg_client.disconnect()
            exit()        
        except errors.AuthKeyPermEmptyError:
            logging.info('The method is unavailable for temporary authorization key, not bound to permanent.')
            return None
        except errors.SessionPasswordNeededError:
            logging.info('Two-steps verification is enabled and a password is required.')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
            exit()
        except errors.UsernameInvalidError:
            logging.info('Nobody is using this username, or the username is unacceptable. If the latter, it must match r"[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]".')
            return None
        except errors.UsernameNotOccupiedError:
            logging.info('The username is not in use by anyone else yet.')
            return None
        except errors.UserDeactivatedError:
            logging.info('User has been deactivate')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            exit()
        except errors.UserDeactivatedBanError:
            logging.info('User has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            exit()
        except errors.AuthKeyUnregisteredError:
            logging.info('AuthKeyUnregisteredError')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
            exit()
        except errors.ChannelsTooMuchError:
            logging.info('You have joined too many channels/supergroups.')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
            exit()
        except errors.ChannelPrivateError:
            logging.info('The channel specified is private and you lack permission to access it. Another reason may be that you were banned from it.')
            return None
        except errors.RPCError: # from https://github.com/LonamiWebs/Telethon/issues/1428 for issue 12
            pass                      
        except errors.ChannelBannedError:
            logging.info('The channel is banned')
            return None
        except errors.ChannelInvalidError:
            logging.info('The channel has invalid error')
            return None          
        except Exception as e:
            logging.info(type(e).__name__)
            return None
        finally:
            db.Close()
            

    async def GetChannels(self):
        channels=[]
        async for dialog in self.tg_client.iter_dialogs():
            if not dialog.is_group and dialog.is_channel:
                channels.append(dialog)
        return channels
