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
    async def test_login(self):
        _join = Join('639657163753')
        self.assertTrue(await _join.Login())


if __name__ == '__main__':
    unittest.main()