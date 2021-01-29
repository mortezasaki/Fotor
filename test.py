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

    def test_Sort(self):
        x = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
        self.assertEqual(utility.SortDic(x), {0: 0, 2: 1, 1: 2, 4: 3, 3: 4})

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
    
    def test_GetPrice(self):
        sms = SMSActivate('376c29Ace3AA9A9f252d2c76c632f0bd')
        self.assertEqual(sms.GetPrice(0),7.00)
        self.assertEqual(sms.GetPrice(1),11.00)
    
    @unittest.skip("Take a long time") 
    def test_SortCountriesByPrice(self):
        sms = SMSActivate('376c29Ace3AA9A9f252d2c76c632f0bd')
        self.assertIsNotNone(sms.SortCountriesByPrice())

    def test_GetNumber(self):
        sms = SMSActivate('376c29Ace3AA9A9f252d2c76c632f0bd')
        self.assertIsNotNone(sms.GetNumber(2))

    @unittest.skip('Take money')
    def test_CancelCode(self):
        sms = SMSActivate('376c29Ace3AA9A9f252d2c76c632f0bd')
        self.assertIsTrue(sms.ConfirmCode('384608665'))

    def test_CancelCode(self):
        sms = SMSActivate('376c29Ace3AA9A9f252d2c76c632f0bd')
        self.assertTrue(sms.CancelCode('384609854'))


if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=ImportWarning)
        unittest.main()