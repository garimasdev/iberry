import traceback
import telegram
from telegram import ParseMode
import traceback
import google.auth
from google.oauth2 import service_account
import google.auth.transport.requests
import requests


# generating a new access token in firebase
def firebase_access_token():
    SERVICE_ACCOUNT_FILE = '/Users/garimasachdeva/Desktop/iberry/iberry/stores/credentials.json'
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
    access_token = 'ya29.c.c0ASRK0GbFRLGdNt-9W6YJjvXJQKjzysxcrMBvasK8o5cOZJEEbHtt2jU8fx7OdjfzdRolftWUJKaQ88-EVvVjvkjlz6N1iQg9-gi4_lgWSFOyTWCp0e2ApoR0MO3cbvB9aQrzr_7KpeVWwwc0RqYjNBWFKgKFSO7ApxbvsNAC7opvpZCMtnn7Wbw-Mo_mPBrWKXkTHBRrHTZC-wenkemxBbkOQibIOE2rN4wmH_WrRra9NDQ3Fw1yQPneocj-tR-Mu_5KsFc2AAR8F7815RCwm5HBS2GCAep4FPWbi5r2NBxF8acAJVvNrYSNwbWjeSFsfBUy5zhOZQ_mvAA3NOIrKyEpKrKVJzlzXga7nGkxUIAJejK-G_nzhAYE384KZQ2c5zoFxds_VMZ34absV7wlOFnwgMq_fiOr19jo8fherhn8IvfkeMqz296zuVYS7qq8QVytheibzMY8wUQFvwQa6zwg5me9nnyJF5XYIFpt1Wzu9ZhRetfYum9Yx6nMBuuZkMtr9rWm1zb45jlhMZ6w62gBs-BR_Bq7lFgMfqnIM90o-u7StSIJFk13zdhIyxzgZ6Rgxdv4VFQaWjQFaleov0Oap1g1oqcb3uSs6htJMbs_36ySc7M5hmnQa-zz7lZRW5-ysh5JkWrjfg98Q73Zx7cZoXwk2B44q6iutnlvRcu__Y8nWzz69e0XMpys_sn_iUF6p41tke6b_B5FkfhI03Z-Fej9Wq92pj8bvVFoimmBs2fhekBZmSZ6z-r9X0dvZ57w43gR32n96Rs2ld55fhR9Yc1S4V47O9FuyJugkrkV_bpefMp6wf5pd6QJMWZ4J6fyMXRRpyZv19l8vUm-tbI9d-ISozpvUmro0wlIjhSF6zWd5tXb3_5hjlSqfOy3s8Ixdbk-vBQzRlsXRMxtq1sdbifBMUnzfdBWubiXkyfFnWza7n2bi_6d1StyF1R6_ttf2z7MRVxRkmaccoB-5bSfomSUtSkolxhnvUXu5xl20atvZht08Rj'
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



