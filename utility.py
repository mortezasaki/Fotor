import re
import requests
import random
import string
from bs4 import BeautifulSoup

def ValidatePhone(phone):
    """Check that phone number is OK

    Args:
        phone (str): phone numer

    Returns:
        [bool]: phone number is OK
    """
    pattern = '^\d{8,}$' # ex: 989161234578
    if re.match(pattern, phone):
        return True

def SortDic(data):
    if data is not None:
        return dict(sorted(data.items(), key=lambda item: item[1]))
    return None

def FakeNameGenerator(gender = 'random', country = 'random'):
    url = 'https://api.namefake.com/api.name-fake.com/{0}/{1}'.format(gender, country)
    req = requests.get(url)
    if req.status_code == 200:
        result = req.json()['name']
        return result
    
    return None

def AndroidDeviceGenerator():
    url = r'https://en.wikipedia.org/wiki/List_of_Android_smartphones'
    req = requests.get(url)
    devices = []
    if req.status_code == 200:
        soup = BeautifulSoup(req.text,'html.parser')
        for device in soup.findAll('th'):
            devices.append(device.text)
        return random.choice(devices)
    return None

# Generate random string https://stackoverflow.com/a/2257449/9850815
def RandomCharacters(size : int = 8, chars = string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
import string
