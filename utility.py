import re
import requests

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