import traceback
import telegram
from telegram import ParseMode
import traceback
import google.auth
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
from decouple  import config



# generating a new access token in firebase
def firebase_access_token():
    creds = {
        "type": config("type", cast=str),
        "project_id": config("project_id",  cast=str),
        "private_key_id": config("private_key_id",  cast=str),
        "private_key": config("private_key",  cast=str),
        "client_email": config("client_email",  cast=str),
        "client_id": config("client_id",  cast=str),
        "auth_uri": config("auth_uri",  cast=str),
        "token_uri": config("token_uri",  cast=str),
        "auth_provider_x509_cert_url": config("auth_provider_x509_cert_url",  cast=str),
        "client_x509_cert_url": config("client_x509_cert_url",  cast=str),
        "universe_domain": config("universe_domain",  cast=str),
    }
    # SERVICE_ACCOUNT_FILE = '/Users/garimasachdeva/Desktop/iberry/iberry/stores/credentials.json'
    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
    credentials = service_account.Credentials.from_service_account_file( creds, scopes=SCOPES)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    access_token = credentials.token
    print(f'Access Token: {access_token}')
    return access_token



# sending a push notification through firebases
def push_notification(body, title, token):
    url = 'https://fcm.googleapis.com/v1/projects/iberry-81920/messages:send'
    access_token = 'ya29.c.c0ASRK0Gbdgd2Nd87YmKFazIwtwv4bkxZEyd2K7wK0oYfuMYMgCy33lPCU7mraioZWN7M7rlJtSopxt4Oi7gYkyaFOJnkKhb1ehAjpqp0dUIeYCWunNukX_NBkh0ncMAftXDJueFhPU9LAgFaMVz9tWRmQBm_B7gTKExpVX4DTCQD-rGVP7nQKJbP_0dH1J-nBOpc1vKdX1U-AwLsmmZscpO6GWAIZdXpFpUG7vpVxj8NUfxjUGZtizgqDiQvJs1iGPhZfPdZ9QTVftkyOoT5DxSiirPREWLpI6B6iZ707E73yQkuaWsDV7Vlc9nKw4_iape1Yr12P3XiQAyMnqR_tET5xEojNMVxICbwN65YhaMbv8wqAULHKLtwN384A2lOWrsnS0rMgoWZM615IQiFZoe5fa01Y6ux4SwWj3th3xVle75snYsdJ79Oozik5r61-0xqhdwp0pXvrcoBU9e2awj8uosp9Mcewr73zlxU-kc7hdgQn-RFq52xgdRcX1X6wkwucucmheJzS8tJua1Vpv5VFzshYybZf4Oki9bxSWpll_k2lwM5ww1t96mmliXryfQgoMgZS5mrXOWsFbJhcmnqu8lvhpi4WdVsgbtV8Xv5o1Mgis-O5jB1lUX4_Jj0nS2OOFrasBfkkBzoSo08_ymRocO9vyya_-kee1smOcBFbQqM3QJUk7MXIRe24xu1da6-ReZYthY3pqp0S250qk1nXZIqn6s3o2xZsms1hhuRMWJdsQepVwlc-7yvx6OQ_5jVM93tSJ96-clQYezo1-lVn8lBoVt07kuBJeW2ohmeRxJt92QyM8Z9sQIw3k-opS2OwO7qQf0f4gMU6FdrohVY1XVOQ0SZcjYIUOSUJ_b4ofUwZtwQk-4iUzMIkFVuxkuvqk43OpgaxXXVbu4ppIFUZleR_iVf9a0SgF02457njusxBtWQakaRbon1c2W4t68RUrXmj6vpZOIS40Js3yoBeq3yB_-vOfIuZ73ucoBwJImq39UgRv29'
    headers  =  {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "message": {
            "token": token,
            "notification": {
                "body": body,
                "title": title
            }
        }
    }
    notification_result = requests.post(url, headers=headers, json=payload)
    if notification_result.status_code == 200:
        return True
    else:
        access_token = firebase_access_token()
        headers  =  {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        notification_result = requests.post(url, headers=headers, json=payload)
        if notification_result.status_code == 200:
            return True
        else:
            return False








# telegram channel notification for all platforms
def telegram_notification(channel_name, bot_token, message):
    try:
        # bot = telegram.Bot(token=settings.TELEGRAM['bot_token'])
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=f'@{channel_name}', text=message,  parse_mode=ParseMode.HTML)
    except:
        traceback.print_exc()



