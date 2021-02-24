import requests
from errors import *
from enums import *
from time import sleep
import logging

class API:

    def __init__(self, phone_number : str):
        self.phone_number = phone_number
        self.api_key = '#$%lkbjflmef158@1!khbdf#$%^&asv@#$%^&ikjbasdk548785asd4f8s4f5sa1f8^ED^SE^&D&^DR*&SDR&F*S^%D*'

    def CallRegisterAPI(self, name : str, family : str, gender : int, country : str, *, status : int, retry : int = 5, wait : float = 3):
        gender = '0' if gender == 'man' else '1'
        url = 'https://api.membersgram.com/api/v2/fotor/register'
        data = {'phonenumber' : self.phone_number,'name' : name, 'status' : status, 'family' : family, 'gender' : gender, 'country' : country, 'apiKey' : self.api_key }
        for i in range(retry):
            try:
                req = requests.post(url, data=data)

                if req.status_code == 200:
                    res_status = req.json()['code']
                    if res_status == RegisterAPIStatus.Succesfull.value:
                        # self.SaveAccountInfo(self.phone_number, name, family, gender, country, str(status), str(res_status))
                        return True
            except ConnectionError:
                logging.info('Exception ConnectionError')
            except Exception as e:
                logging.info(type(e).__name__)            
            sleep(wait)
        return False
        # raise FaildAPIConnection() # Error when can't connect to Membersgram api

    def CallGetChannel(self):
        url = 'https://api.membersgram.com/api/v2/fotor/getChannel/%s' % self.phone_number
        data = {'apiKey' : self.api_key }
        try:
            req = requests.post(url, data=data)

            if req.status_code == 200:
                return req.json()['data']
        except ConnectionError:
            logging.info("Can't connect to Membersgram Server")
            return None
        except Exception as e:
            logging.info(type(e).__name__, ' CallGetChannel')
        return None

    def CallJoin(self, _id : str):
        url = 'https://api.membersgram.com/api/v2/fotor/joinChannel/{0}/{1}'.format(_id, self.phone_number)
        data = {'apiKey' : self.api_key }
        try:
            req = requests.post(url, data=data)

            if req.status_code == 200:
                res = req.json()['code']
                if res == 200:
                    return True
        except ConnectionError:
            logging.info("Can't connect to Membersgram Server")
            return False
        except Exception as e:
            logging.info(type(e).__name__, ' CallJoin')                          
            return False
        return False


    def SaveAccountInfo(self, *argv):
        with open('Accounts/%s/info.txt' %(self.phone_number),'w') as f:
            f.write('\n'.join(argv))