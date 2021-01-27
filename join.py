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
import os
import asyncio

class Join:
    def __init__(self, phone_number : str):
        self.loop = asyncio.get_event_loop()
        self.phone_number = phone_number
        self.client = ''

    async def Login(self):
        tg_session_location = '{0}{1}.session'.format(Config['account_path'],phone_number)
        if os.path.exists(tg_session_location):
            self.client = TelegramClient(tg_session_location, Config['tg_api_id'], Config['tg_api_hash'])
            if self.client.is_connected():
                return True
            return False
