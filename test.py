import unittest
import utility
from join import Join, SMSActivate
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

class TestSMSActivate(unittest.TestCase):
    def test_Balance(self):
        sms = SMSActivate('376c29Ace3AA9A9f252d2c76c632f0bd')
        self.assertEqual(sms.Balance(), 389.98)

    def test_GetCountry(self):
        sms = SMSActivate('376c29Ace3AA9A9f252d2c76c632f0bd')
        self.assertIsNotNone(sms.GetCountry())


if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=ImportWarning)
        unittest.main()