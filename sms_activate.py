import utility
from config import Config
import logging
import requests
import re
from time import sleep
from enums import SMSActivateSMSStatus

class SMSActivate:
    def __init__(self, api_key : str):
        self.api_key = api_key
        self.countries = {}
        
    def Balance(self):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key=%s&action=getBalance' % self.api_key
        req = requests.get(url)

        if req.status_code == 200: 
            res = req.text
            pattern = r'^(ACCESS_BALANCE:)\d+(\.\d+)?$'
            if re.match(pattern, res): # Example ACCESS_BALANCE:389.98%
                try:
                    balance = float(res.split(':')[1])
                    return balance
                except:
                    logging.info("Can't extract balance")
        
        return False

    def GetCountry(self):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key=%s&action=getCountries' % self.api_key
        req = requests.get(url)

        if req.status_code == 200:
            try: 
                res = req.json()
                for _id,names in res.items():
                    self.countries[_id] =  names['eng']
                return self.countries
            except:
                return None
        else:
            return None

    def GetPrice(self, country_code, service : str = 'tg'):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key={0}&action=getPrices&service={1}&country={2}'.format(self.api_key, service, country_code)
        req = requests.get(url)        

        if req.status_code == 200:
            try:
                res = req.json()
                return res[str(country_code)][service]['cost']
            except:
                return None
        return None

    def SortCountriesByPrice(self, cost_threshold = 20, limit = 20):
        countries = self.GetCountry()

        if countries is not None:
            costs = {}
            count = 0
            for country in countries.keys():
                if count < limit or limit <= 0:
                    count+=1
                else:
                    break
                price = self.GetPrice(country)
                if price is not None and price <= cost_threshold:
                    costs[country] = price
            sorted_costs = utility.SortDic(costs)
            return sorted_costs
        return None

    def GetNumber(self, country_code, service= 'tg', retry : int = 5, wait : float = 3):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key={0}&action=getNumber&service={1}&country={2}'.format(self.api_key, service, country_code)
        # Fix bug 34
        bad_phonenumber =[
            '6283'
        ]
        for i in range(retry):
            req = requests.get(url)        

            if req.status_code == 200:
                try:
                    response = req.text
                    pattern = r'^(ACCESS_NUMBER:)\d{8,}(:)\d{8,}$'
                    if re.match(pattern, response):
                        status_code = response.split(':')[1]
                        phone_number = response.split(':')[2]
                        # Fix bug 34
                        bad_phone = False
                        for phone in bad_phonenumber:
                            if phone_number.startswith(phone):
                                sleep(wait)
                                bad_phone = True
                        if not bad_phone:
                            return {'Status' : status_code, 'Phone' : phone_number}
                    elif 'BANNED' in response:
                        sleep(60)
                except Exception as e:
                    logging.info(type(e).__name__)
                    return None
            sleep(wait)
        return None

    def ChangeNumberStatus(self,id, status):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key={0}&action=setStatus&status={1}&id={2}'.format(self.api_key, status, id)
        req = requests.get(url)        

        if req.status_code == 200:
            return req.text
        return None

    def ConfirmCode(self, id):
        result = self.ChangeNumberStatus(id, SMSActivateSMSStatus.Complate.value)
        if result is not None and result == 'ACCESS_ACTIVATION':
            return True
        return False
    
    def CancelCode(self, id):
        result = self.ChangeNumberStatus(id, SMSActivateSMSStatus.Cancel.value)
        if result is not None and result == 'ACCESS_CANCEL':
            return True
        return False

    def GetActivationCode(self, id, *, retry : int = 10, wait : float = 5):
        url = 'https://sms-activate.ru/stubs/handler_api.php?api_key={0}&action=getStatus&id={1}'.format(self.api_key, id)
        for i in range(retry):
            req = requests.get(url)        

            if req.status_code == 200:
                pattern = r'^(STATUS_OK:)\d{5}$' # ex STATUS_OK:20980
                if re.match(pattern, req.text):
                    return req.text.split(':')[1]
            sleep(wait)
        return None
    
    def GetCountryName(self, _id : int):
        if _id in self.countries.keys():
            return self.countries[_id]
        return None