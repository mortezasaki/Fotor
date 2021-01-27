import unittest
import utility
from join import Join
import asyncio
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

    async def test_login(self):
        self.assertTrue(await self.join.Login())

    def test_valid_username(self):
        self.assertTrue(self.join.ValidUsername('Morteza'))
        self.assertTrue(self.join.ValidUsername('Mor43443'))
        self.assertFalse(self.join.ValidUsername('1234344'))
        self.assertFalse(self.join.ValidUsername('dsfd'))

if __name__ == '__main__':
    unittest.main()