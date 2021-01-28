import unittest
import utility
from join import Join
import asyncio
import warnings
class TestUtility(unittest.TestCase):
    def test_ValidatePhone(self):
        self.assertTrue(utility.ValidatePhone('989161234578'))
        self.assertFalse(utility.ValidatePhone('test'))
        self.assertFalse(utility.ValidatePhone('Test989161234578'))
        self.assertFalse(utility.ValidatePhone('98916'))
        self.assertFalse(utility.ValidatePhone('98916test8'))

class TestJoin(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestJoin, self).__init__(*args, **kwargs)
        self.join = Join('639657163753')

    def test_valid_username(self):
        self.assertTrue(self.join.ValidUsername('Morteza'))
        self.assertTrue(self.join.ValidUsername('Mor43443'))
        self.assertFalse(self.join.ValidUsername('1234344'))
        self.assertFalse(self.join.ValidUsername('dsfd'))
        self.assertFalse(self.join.ValidUsername('12As'))

    def test_login(self):
        self.assertTrue(self.join.Login())

    def test_search(self):
        self.assertIsNotNone(self.join.Search('membersgram_app'))
        self.assertIsNone(self.join.Search('12As'))
        self.assertIsNone(self.join.Search('fdsfdfdsfdsfdshgdfwewsdf'))
    
    async def test_Login(self):
        await self.assertIsNotNone(await self.join.Search('membersgram_app'))
        await self.assertIsNone(await self.join.Search('12As'))
        await self.assertIsNone(await self.join.Search('fdsfdfdsfdsfdshgdfwewsdf'))    

    async def test_get_channel(self):
        await self.assertIsNotNone(self.join.GetChannels())



if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=ImportWarning)
        unittest.main()