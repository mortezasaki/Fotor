import os
from config import Config
import sys
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon import errors, functions
import asyncio
import utility
import logging
import socks
import re
from time import sleep
from enums import *
from database import Database
import sqlite3
import random
from pytz import timezone, utc
from datetime import datetime

def LogInit():
    # output log on stdout https://stackoverflow.com/a/14058475/9850815
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_file_name = 'logs/telegram.log'

    logging.basicConfig(filename=log_file_name, filemode="a", level=logging.INFO,format = '%(asctime)s - %(message)s') 

    logging.Formatter.converter = customTime

# Use custom timezone in logging https://stackoverflow.com/a/45805464/9850815
def customTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone("Asia/Tehran")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()

class Telegram:
    def __init__(self, phone_number):
        LogInit()
        self.phone_number = phone_number
        if not os.path.exists(Config['account_path']):
            os.makedirs(Config['account_path'])

        self.tg_client = ''

    @staticmethod
    def ValidUsername(username : str):
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
        except Exception as e:
            logging.info(type(e).__name__, 'telegram SignUp')
            return False

    async def Connect(self, use_proxy = False, login = True):
        tg_session_location = '{0}{1}.session'.format(Config['account_path'],self.phone_number)
        if login and not os.path.exists(tg_session_location):
            sys.exit()

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
                sys.exit()
            except SystemExit():
                sys.exit()
        
        try:
            await self.tg_client.connect()
            if self.tg_client.is_connected() :
                return True
        except errors.TimeoutError:
            logging.info('Fail to connect.')
            return False
        except Exception as e:
            logging.info(type(e).__name__, ' Connect')
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
                logging.info('Flood wait for %s', e.seconds)
                logging.info('Exit...')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
                db.UpdateFlooWait(self.phone_number, e.seconds)
                await self.tg_client.disconnect()
                sys.exit()
            except errors.UserDeactivatedBanError:
                logging.info('The user has been banned')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
                sys.exit()
            except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
                logging.info('Account has auth problem')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
                sys.exit()
            except errors.SessionPasswordNeededError: # TODO: Handle when account has password
                logging.info('Account has password')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
                sys.exit()
            except errors.ChannelsTooMuchError:
                logging.info('You have joined too many channels/supergroups.')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
                sys.exit()
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
            except errors.SessionPasswordNeededError: # Fix issue 23
                logging.info('Two-steps verification is enabled and a password is required')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)           
                sys.exit()                
            except sqlite3.OperationalError:
                logging.info('sqlite OperationalError on Resolve')
                return None                              
            except Exception as e:
                logging.info(type(e).__name__, ' Search Channel')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.Stop.value)
                sys.exit()              
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
                logging.info('Flood wait for %s', e.seconds)
                logging.info('Exit...')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
                db.UpdateFlooWait(self.phone_number, e.seconds)
                await self.tg_client.disconnect()
                sys.exit()
            except errors.UserDeactivatedBanError:
                logging.info('The user has been banned')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
                sys.exit()
            except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
                logging.info('Account has auth problem')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
                os.remove('{0}{1}.session'.format(Config['account_path'], self.phone_number))
                sys.exit()

            except errors.SessionPasswordNeededError: # TODO: Handle when account has password
                logging.info('Account has password')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
                sys.exit()
            except errors.ChannelsTooMuchError:
                logging.info('You have joined too many channels/supergroups.')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
                sys.exit()
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
            except sqlite3.OperationalError:
                logging.info('sqlite OperationalError on Resolve')
                return None
            except errors.SessionPasswordNeededError: # Fix issue 23
                logging.info('Two-steps verification is enabled and a password is required')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)           
                sys.exit()
            except Exception as e:
                logging.info(type(e).__name__, ' JoinChannel')
                db.UpdateStatus(self.phone_number, TelegramRegisterStats.Stop.value)
                sys.exit()
            finally:
                db.Close()               
        return None

    async def Resolve(self, username : str):
        db = Database()
        try:
            return await self.tg_client(functions.contacts.ResolveUsernameRequest(username))
        except errors.FloodWaitError as e:
            logging.info('Flood wait for %s', e.seconds)
            logging.info('Exit...')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
            db.UpdateFlooWait(self.phone_number, e.seconds)
            await self.tg_client.disconnect()
            sys.exit()        
        except errors.AuthKeyPermEmptyError:
            logging.info('The method is unavailable for temporary authorization key, not bound to permanent.')
            return None
        except errors.SessionPasswordNeededError:
            logging.info('Two-steps verification is enabled and a password is required.')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
            sys.exit()
        except errors.UsernameInvalidError:
            logging.info('Nobody is using this username, or the username is unacceptable. If the latter, it must match r"[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]".')
            return None
        except errors.UsernameNotOccupiedError:
            logging.info('The username is not in use by anyone else yet.')
            return None
        except errors.UserDeactivatedError:
            logging.info('User has been deactivate')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('User has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.AuthKeyUnregisteredError:
            logging.info('AuthKeyUnregisteredError')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
            sys.exit()
        except errors.ChannelsTooMuchError:
            logging.info('You have joined too many channels/supergroups.')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
            sys.exit()
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
        except sqlite3.OperationalError:
            logging.info('sqlite OperationalError on Resolve')
            return None
        except errors.SessionPasswordNeededError: # Fix issue 23
            logging.info('Two-steps verification is enabled and a password is required')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)           
            sys.exit()            
        except Exception as e:
            logging.info(type(e).__name__, ' Resolve')
            return None
        finally:
            db.Close()
            
    async def JoinGroup(self, group_hash):
        try:
            db = Database()
            return await self.tg_client(functions.messages.ImportChatInviteRequest(
                hash = group_hash))
        except errors.ChannelsTooMuchError:
            logging.info('You have joined too many channels/supergroups.')
        except errors.InviteHashEmptyError:
            logging.info('The invite hash is empty.')
        except errors.InviteHashExpiredError:
            logging.info('The chat the user tried to join has expired and is not valid anymore.')
        except errors.InviteHashInvalidError:
            logging.info('The invite hash is invalid.')                        
        except errors.SessionPasswordNeededError:
            logging.info('Two-steps verification is enabled and a password is required.')            
        except errors.UsersTooMuchError	:
            logging.info('The maximum number of users has been exceeded (to create a chat, for example).')            
        except errors.UserAlreadyParticipantError	:
            logging.info('The authenticated user is already a participant of the chat.')            
        except errors.FloodWaitError as e:
            logging.info('Flood wait for %s', e.seconds)
            logging.info('Exit...')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
            db.UpdateFlooWait(self.phone_number, e.seconds)
            await self.tg_client.disconnect()
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('The user has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
            logging.info('Account has auth problem')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
            os.remove('{0}{1}.session'.format(Config['account_path'], self.phone_number))
            sys.exit()
        except errors.SessionPasswordNeededError: # TODO: Handle when account has password
            logging.info('Account has password')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
            sys.exit()
        except errors.ChannelsTooMuchError:
            logging.info('You have joined too many channels/supergroups.')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
            sys.exit()
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
        except sqlite3.OperationalError:
            logging.info('sqlite OperationalError on Resolve')
            return None
        except errors.SessionPasswordNeededError: # Fix issue 23
            logging.info('Two-steps verification is enabled and a password is required')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)           
            sys.exit()
        except Exception as e:
            logging.info(type(e).__name__, ' JoinChannel')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Stop.value)
            sys.exit()
        finally:
            db.Close()                            
        
        return None

    async def GetChannels(self):
        channels=[]
        async for dialog in self.tg_client.iter_dialogs():
            if not dialog.is_group and dialog.is_channel:
                channels.append(dialog)
        return channels

    async def SetUserName(self, username):
        try:
            await self.tg_client(functions.account.UpdateUsernameRequest(username = username))
            return True
        except errors.UsernameInvalidError:
            logging.info('Nobody is using this username, or the username is unacceptable. If the latter, it must match r"[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]".')
        except errors.UsernameNotModifiedError:
            logging.info('The username is not different from the current username.')
        except errors.UsernameOccupiedError:
            logging.info('The username is already taken.')
        except Exception as e:
            logging.info(type(e).__name__, 'SetUserName')
        
        return False

    async def SetBio(self, bio):
        try:
            await self.tg_client(functions.account.UpdateProfileRequest(about = bio))
            return True
        except errors.AboutTooLongError:
            logging.info('The provided bio is too long.')
        except Exception as e:
            logging.info(type(e).__name__, 'SetBio')   
        
        return False

    async def SetProfileImage(self, img_address):
        try:
            await self.tg_client(functions.photos.UploadProfilePhotoRequest(
                file = await self.tg_client.upload_file(img_address)
            ))
            return True
        except errors.AlbumPhotosTooManyError:
            logging.info('Too many photos were included in the album.')
        except errors.FilePartsInvalidError:
            logging.info('The number of file parts is invalid.')
        except errors.ImageProcessFailedError:
            logging.info('Failure while processing image.')
        except errors.PhotoCropSizeSmallError:
            logging.info('Photo is too small.')
        except errors.PhotoExtInvalidError:
            logging.info('The extension of the photo is invalid.')
        except errors.VideoFileInvalidError:
            logging.info('The given video cannot be used.')
        except Exception as e:
            logging.info(type(e).__name__, 'SetProfileImage')
        
        return False

    async def SendMessage(self, receptor, message):
        try:
            db = Database()
            entity= await self.tg_client.get_entity(receptor)
            reply = random.choice([0,1])
            if reply == 0 : # No replay a message
                await self.tg_client.send_message(entity=entity,message = message)
            else:
                messages = await self.GetMessage(entity)
                msg_id = random.choice(messages).id
                await self.tg_client.send_message(entity=entity,message = message, reply_to = msg_id)               
            return True
        except errors.UsernameNotOccupiedError:
            logging.info('The username is not in use by anyone else yet (caused by ResolveUsernameRequest)')
        except errors.UserDeactivatedError:
            logging.info('User has been deactivate')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('User has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()            
        except ValueError:
            logging.info('Cannot get entity from a channel (or group) that you are not part of. Join the group and retry')
            group_hash = r'IPiIQKTNSnm7_lPk'
            await self.JoinGroup(group_hash)
            logging.info('Joining to Phoenix group')   
        except errors.FloodWaitError as e:
            logging.info('Flood wait for %s', e.seconds)
            logging.info('Exit...')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
            db.UpdateFlooWait(self.phone_number, e.seconds)
            await self.tg_client.disconnect()
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('The user has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
            logging.info('Account has auth problem')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
            os.remove('{0}{1}.session'.format(Config['account_path'], self.phone_number))
            sys.exit()
        except errors.SessionPasswordNeededError: # TODO: Handle when account has password
            logging.info('Account has password')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
            sys.exit()
        except errors.ChannelsTooMuchError:
            logging.info('You have joined too many channels/supergroups.')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
            sys.exit()
        except errors.ChannelPrivateError:
            logging.info('The channel specified is private and you lack permission to access it. Another reason may be that you were banned from it.')
        except errors.RPCError: # from https://github.com/LonamiWebs/Telethon/issues/1428 for issue 12
            pass
        except errors.ChannelBannedError:
            logging.info('The channel is banned')
        except errors.ChannelInvalidError:
            logging.info('The channel has invalid error')
        except sqlite3.OperationalError:
            logging.info('sqlite OperationalError on Resolve')
        except errors.SessionPasswordNeededError: # Fix issue 23
            logging.info('Two-steps verification is enabled and a password is required')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)           
            sys.exit()
        except Exception as e:
            logging.info(type(e).__name__, ' SendMessage')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Stop.value)
        finally:
            db.Close()                                    
        return False

    async def SendFile(self, receptor, file_address):
        try:
            db = Database()
            entity= await self.tg_client.get_entity(receptor)
            reply = random.choice([0,1])
            if reply == 0 : # No replay a message
                await self.tg_client.send_file(entity, file_address)
            else:
                messages = await self.GetMessage(entity)
                msg_id = random.choice(messages).id
                await self.tg_client.send_file(entity, file_address, reply_to = msg_id)
            return True
        except errors.UserDeactivatedError:
            logging.info('User has been deactivate')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('User has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()                  
        except ValueError:
            logging.info('Cannot get entity from a channel (or group) that you are not part of. Join the group and retry')
            group_hash = r'IPiIQKTNSnm7_lPk'
            await self.JoinGroup(group_hash)
            logging.info('Joining to Phoenix group')            
        except errors.FloodWaitError as e:
            logging.info('Flood wait for %s', e.seconds)
            logging.info('Exit...')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
            db.UpdateFlooWait(self.phone_number, e.seconds)
            await self.tg_client.disconnect()
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('The user has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
            logging.info('Account has auth problem')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
            os.remove('{0}{1}.session'.format(Config['account_path'], self.phone_number))
            sys.exit()
        except errors.SessionPasswordNeededError: # TODO: Handle when account has password
            logging.info('Account has password')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
            sys.exit()
        except errors.ChannelsTooMuchError:
            logging.info('You have joined too many channels/supergroups.')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
            sys.exit()
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
        except sqlite3.OperationalError:
            logging.info('sqlite OperationalError on Resolve')
            return None
        except errors.SessionPasswordNeededError: # Fix issue 23
            logging.info('Two-steps verification is enabled and a password is required')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)           
            sys.exit()
        except Exception as e:
            logging.info(type(e).__name__, ' SendFile')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Stop.value)            
        return False

    async def GetMessage(self, chat):
        try:
            db = Database()
            entity= await self.tg_client.get_entity(chat)
            messages = await self.tg_client.get_messages(entity, limit = 5)
            return messages
        except errors.UserDeactivatedError:
            logging.info('User has been deactivate')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('User has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except ValueError:
            logging.info('Cannot get entity from a channel (or group) that you are not part of. Join the group and retry')
            group_hash = r'IPiIQKTNSnm7_lPk'
            await self.JoinGroup(group_hash)
            logging.info('Joining to Phoenix group')
        except errors.FloodWaitError as e:
            logging.info('Flood wait for %s', e.seconds)
            logging.info('Exit...')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
            db.UpdateFlooWait(self.phone_number, e.seconds)
            await self.tg_client.disconnect()
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('The user has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
            logging.info('Account has auth problem')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
            os.remove('{0}{1}.session'.format(Config['account_path'], self.phone_number))
            sys.exit()
        except errors.SessionPasswordNeededError: # TODO: Handle when account has password
            logging.info('Account has password')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
            sys.exit()
        except errors.ChannelsTooMuchError:
            logging.info('You have joined too many channels/supergroups.')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
            sys.exit()
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
        except sqlite3.OperationalError:
            logging.info('sqlite OperationalError on Resolve')
            return None
        except errors.SessionPasswordNeededError: # Fix issue 23
            logging.info('Two-steps verification is enabled and a password is required')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)           
            sys.exit()
        except Exception as e:
            logging.info(type(e).__name__, ' SendFile')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Stop.value)             
        
        return None

    async def ForwardMessage(self, chat, message):
        try:
            db = Database()
            entity= await self.tg_client.get_entity(chat)
            return await self.tg_client.forward_messages(entity, message)
        except errors.UserDeactivatedError:
            logging.info('User has been deactivate')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('User has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except ValueError:
            logging.info('Cannot get entity from a channel (or group) that you are not part of. Join the group and retry')
            group_hash = r'IPiIQKTNSnm7_lPk'
            await self.JoinGroup(group_hash)
            logging.info('Joining to Phoenix group')  
        except errors.FloodWaitError as e:
            logging.info('Flood wait for %s', e.seconds)
            logging.info('Exit...')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.FloodWait.value)
            db.UpdateFlooWait(self.phone_number, e.seconds)
            await self.tg_client.disconnect()
            sys.exit()
        except errors.UserDeactivatedBanError:
            logging.info('The user has been banned')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Ban.value)
            sys.exit()
        except errors.AuthKeyUnregisteredError: # this error accurrd when sing up another system and try login from this system
            logging.info('Account has auth problem')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.AuthProblem.value)
            os.remove('{0}{1}.session'.format(Config['account_path'], self.phone_number))
            sys.exit()
        except errors.SessionPasswordNeededError: # TODO: Handle when account has password
            logging.info('Account has password')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)
            sys.exit()
        except errors.ChannelsTooMuchError:
            logging.info('You have joined too many channels/supergroups.')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.ToMany.value)
            sys.exit()
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
        except sqlite3.OperationalError:
            logging.info('sqlite OperationalError on Resolve')
            return None
        except errors.SessionPasswordNeededError: # Fix issue 23
            logging.info('Two-steps verification is enabled and a password is required')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.HasPassword.value)           
            sys.exit()
        except TypeError:
            logging.info('Type error in %s', 'ForwardMessage')
        except Exception as e:
            logging.info(type(e).__name__, 'ForwardMessage')
            db.UpdateStatus(self.phone_number, TelegramRegisterStats.Stop.value)                                    
        return None
