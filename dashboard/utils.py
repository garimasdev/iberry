import requests
from django.urls import reverse
from urllib.parse import urlencode
import random
import string

def getShortUrl(room_token):
    url = "https://curt.shop/"
    # api_url = reverse('qr_login', args=[room_token])  # Assuming 'qr_login' is the URL name for qr/login/
    # print(api_url)
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "mode": "api",
        # "url": "https://demo.iberrywifi.in/store/"+room_token+"/",
        "url": "https://iberry.caucasianbarrels.com/store/"+room_token+"/",
    }
    
    encoded_data = urlencode(data)
    print(f"Encoded data: {encoded_data}")
    response = requests.post(url, headers=headers, data=data, verify=False)
    result = response.json()
    
    return result



def generateAuthToken():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return random_string