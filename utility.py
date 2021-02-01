import re
import requests
import random
import string
from bs4 import BeautifulSoup
from time import sleep

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

def GetProxy(retry : int = 5, wait : float = 5, method : int = 0):
    # country that Censorship Telegram https://en.wikipedia.org/wiki/Telegram_(software)#Censorship
    country_ignore = ['RU', 'IR' , 'CN', 'PK', 'AZ' , 'BH', 'BY', 'HK', 'IN', 'ID', 'TH']

    if method == 0:
        for i in range(retry):
            req = requests.get('https://spys.me/proxy.txt')
            if req.status_code == 200:
                proxy_pattern = r'((?:[0-9]{1,3}\.){3}[0-9]{1,3})(:)(\d{2,5})( )(\w{2})'
                proxies = re.findall(proxy_pattern, req.text)

                proxyList = []
                for proxy in proxies:
                    if proxy[4] not in country_ignore:
                        proxyList.append({'IP' : proxy[0], 'Port' : proxy[2], 'Country' : proxy[4]})

                return proxyList

            sleep(wait)
            

    elif method == 1:
        url = r'http://www.freeproxylists.net/?c=&pt=&pr=HTTPS&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0'
        for i in range(retry):
            req = requests.get(url)
            if req.status_code == 200:
                text = req.text
                soup = BeautifulSoup(text, 'html.parser')                
                rows = soup.findAll('tr')
                for row in rows[1:]:
                    # if not random.choice([True, False]): # for randomize selction proxy
                    #     continue
                    cols = row.findAll('td')
                    if len(cols)>1:
                        # matching IPv4 Addresss https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch07s16.html
                        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
                        port_pattern = r'\d{4,5}'
                        ip = cols[0].find('a').text
                        port = cols[1].text
                        if re.match(ip_pattern, ip) and re.match(port_pattern, port):
                            return {'IP' : ip, 'Port' : port}        
    elif method == 2:
        url = r'https://www.sslproxies.org/'
        for i in range(retry):
            req = requests.get(url)
            if req.status_code == 200:
                text = req.text
                soup = BeautifulSoup(text, 'html.parser')
                rows = soup.findAll('tr')
                for row in rows[1:]:
                    if not random.choice([True, False]): # for randomize selction proxy
                        continue
                    cols = row.findAll('td')
                    if len(cols)>1:
                        # matching IPv4 Addresss https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch07s16.html
                        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
                        port_pattern = r'\d{4,5}'
                        ip = cols[0].text
                        port = cols[1].text
                        if re.match(ip_pattern, ip) and re.match(port_pattern, port):
                            return {'IP' : ip, 'Port' : port}
    elif method == 3:
        url = r'https://spys.one/en/socks-proxy-list/'
        for i in range(retry):
            req = requests.get(url)
            if req.status_code == 200:
                text = req.text
                soup = BeautifulSoup(text, 'html.parser')
                rows = soup.findAll('tr')
                for row in rows[1:]:
                    if not random.choice([True, False]): # for randomize selction proxy
                        continue
                    cols = row.findAll('td')
                    if len(cols)>1:
                        # matching IPv4 Addresss https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch07s16.html
                        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
                        port_pattern = r'\d{4,5}'
                        ip = cols[0].findAll('font')
                        port = ip[1].text
                        ip = ip[0].text
                        if re.match(ip_pattern, ip) and re.match(port_pattern, port):
                            return {'IP' : ip, 'Port' : port}
    
    return None