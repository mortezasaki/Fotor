import requests
from telethon import TelegramClient
import asyncio
from telethon import functions, types
from telethon.tl.functions.channels import JoinChannelRequest
import time
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.contacts import AddContactRequest,GetContactsRequest
from telethon.tl.functions.messages import SendMessageRequest


loop = asyncio.get_event_loop()

api_id = 21724
api_hash = '3e0cb5efcd52300aec5994fdfc5bdc16'
apiKey = "#$%lkbjflmef158@1!khbdf#$%^&asv@#$%^&ikjbasdk548785asd4f8s4f5sa1f8^ED^SE^&D&^DR*&SDR&F*S^%D*" #api key for membersgram
API_Key = "376c29Ace3AA9A9f252d2c76c632f0bd" # sms-activate api key

country=6




# start register in telegram

async def test():
    
    # send Request for Get phonenumber 

    while True : 

        url_get_phonenumber = "https://sms-activate.ru/stubs/handler_api.php?api_key="+API_Key+"&action=getNumber&service=tg&country="+str(country)
        response_get_phonenumber = requests.post(url_get_phonenumber)
        response_get_phonenumber = response_get_phonenumber.text.split(":")
        if len(response_get_phonenumber) < 1 :
            print("cant get phonenumber")
            exit(0)

        print("response_get_phonenumber")
        print(response_get_phonenumber)
        if response_get_phonenumber[0] == "NO_NUMBERS":
            print("cant get phonenumber")
        else :
            phonenumber = response_get_phonenumber[2]
            phonenumber_id = response_get_phonenumber[1]
            break

    # end code for get phonenumber

    
    client= TelegramClient(phonenumber, api_id, api_hash)
    await client.connect()
    await client.send_code_request(phonenumber)

    print('code send by telegram')
    
    loop_i = 0
    activate_code = ""
    print("loop for get active")
    while True:
        request_get_activate_code = requests.post("https://sms-activate.ru/stubs/handler_api.php?api_key="+API_Key+"&action=getStatus&id="+phonenumber_id)
        # STATUS_OK:42305 or STATUS_WAIT_CODE
        request_get_activate_code = request_get_activate_code.text
        print("request_get_activate_code")
        print(request_get_activate_code)
        if request_get_activate_code != "STATUS_WAIT_CODE":
            activate_code = request_get_activate_code.split(":")[1]
            print("activate code is ==> " + activate_code)
            break
        loop_i +=1
        time.sleep(4)

    if len(activate_code) < 1 :
        print("cant get activate code")
        exit(0);


    await client.sign_up(activate_code, first_name='hassan', last_name='ahmadof')




    while True :
        search = input('enter search: ')    
        channel = await client.get_entity(search)
        print(channel)
        messages = await client.get_messages(channel, limit= 1) 
        print(messages)

        await client(JoinChannelRequest(search))
# 

loop.run_until_complete(test())