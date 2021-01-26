

from telethon import TelegramClient
api_id = 21724
api_hash = '3e0cb5efcd52300aec5994fdfc5bdc16'
import asyncio
loop = asyncio.get_event_loop()
from telethon import functions, types
from telethon.tl.functions.channels import JoinChannelRequest
import time
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.contacts import AddContactRequest,GetContactsRequest
from telethon.tl.functions.messages import SendMessageRequest

from telethon.tl.functions import *



async def test():
    client= TelegramClient('Telegram android x', api_id, api_hash)
    await client.connect()
    phone = '+6283844185816'
    # sender1 = await client.send_code_request(phone)
    # if sender1.timeout != None :
    #     time.sleep(sender1.timeout)
    # print(sender1)

    # sender2 = await client(functions.auth.ResendCodeRequest(phone,sender1.phone_code_hash))
    # print(sender2)

    # if sender2.timeout != None :
    #     time.sleep(sender2.timeout)

    # sender3 = await client(functions.auth.ResendCodeRequest(phone,sender1.phone_code_hash))

    # print(sender3)
    await client.send_code_request(phone)

    code = input('enter code: ')
    # password = input('enter password: ')
    await client.sign_up(code, first_name='fotor', last_name='Banana')
    # await client.sign_in(phone=phone,code=code,password=password,phone_code_hash=sender1.phone_code_hash);
    # Ensure you're authorized
    # if not client.is_user_authorized():
    # sender1 = await client.send_code_request(phone)
    # if sender1.timeout != None :
    #     time.sleep(sender1.timeout)
    # print(sender1)
    # try:
    #     await client.sign_in(phone, input('Enter the code: '))
    #     # me = client.get_me()

    # except SessionPasswordNeededError:
    #     await client.sign_in(password=input('Password: '))
    #     # me = client.get_me()

    #     # print(me)
    time.sleep(10)


    # sendmessage = await client(SendMessageRequest('mohammad_m96', 'Hello there!'))

    while True :
        search = input('enter search: ')    
        channel = await client.get_entity(search)
        print(channel)
        messages = await client.get_messages(channel, limit= 1) 
        print(messages)

        # await client(JoinChannelRequest(search))
    


loop.run_until_complete(test())
