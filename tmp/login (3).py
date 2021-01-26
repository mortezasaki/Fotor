

from telethon import TelegramClient
api_id = 21724
api_hash = '3e0cb5efcd52300aec5994fdfc5bdc16'
import asyncio
loop = asyncio.get_event_loop()
from telethon import functions, types
from telethon.tl.functions.channels import JoinChannelRequest
import time
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

async def test():
    client= TelegramClient('Telegram android x', api_id, api_hash)
    await client.connect()
    
    while True :
        search = input('enter search: ')    
        channel = await client.get_entity(search)
        print("channel")
        print(channel)
        await client.get_messages(channel, limit= 1) 
        print("messages")

        await client(JoinChannelRequest(search))
    
# send message
    # time.sleep(10)

    # sendmessage = await client(SendMessageRequest('mohammad_m96', 'Hello there!'))

# send message ended

# update profile

    # await client(UploadProfilePhotoRequest(
    #     await client.upload_file('./1.jpg')
    # ))

# end update profile


    # time.sleep(10)


# update profile end

# join channel
    # while True :
        # search = input('enter search: ')
        # newjoin = await client(JoinChannelRequest(search))
        # print(newjoin)
        # time.sleep(4)
# 
# join channel end!
    

# join channel

    # while True :
        # search = input('enter search: ')
        # result = await client(functions.contacts.SearchRequest(
        #     q=search,
        #     limit=1
        # ))
        # print(result)

        # await client(JoinChannelRequest(search))

# end joinschannel


loop.run_until_complete(test())