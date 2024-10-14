import traceback
import telegram
from telegram import ParseMode
import traceback
import google.auth
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import os
from  django.conf import settings
from decouple import config


# generating a new access token in firebase
def firebase_access_token():
    SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, "stores", "credentials.json")
    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
    credentials = service_account.Credentials.from_service_account_file( SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    access_token = credentials.token
    print(f'Access Token: {access_token}')
    return access_token



# sending a push notification through firebases
def push_notification(body, title, token):
    url = 'https://fcm.googleapis.com/v1/projects/iberry-81920/messages:send'
    access_token = config("access_token", cast=str)
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








# telegram channel for room orders notification 
def telegram_notification(channel_name, bot_token, message):
    try:
        # bot token and channel name from room model
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=f'@{channel_name}', text=message,  parse_mode=ParseMode.HTML)
    except:
        traceback.print_exc()

# exception telegram channel
def telegram_exception(message):
    try:
        bot_token = telegram.Bot(token=settings.TELEGRAM['bot_token'])
        channel_name = settings.TELEGRAM['channel_name']
        bot_token.send_message(chat_id=channel_name, text=message, parse_mode=ParseMode.HTML)
    except:
        traceback.print_exc()
        



