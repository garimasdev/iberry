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
    access_token = 'ya29.c.c0ASRK0GZQpK6oZ4pwd_9lmB5KZuV4HeD9csGAcc0QpLQzqtg0pDTrhGsKhsSr3liwJ7a5Bgo6hOUUR4GKgB6QjsKNAckyr2CJdihqJlHj1o76J7BHUcqrLboSTlkRpsXvSu0y1LkGUIEtZ5hfxHNvZhi4PGlPGfrzaQBjDru8Jia7pSDzQ7-gnMhGspy2lM59DbS8-4X3BEbFBd-Uzbl444VwQ_kJ-1jqveLIX0q-thGnWpRIxOgJTZjmknLES-SaTavdIXUsWm3L3C546VyoYW9TamCTyciZ4M9b5rSWHZsUrgHZvfTwU8gEO1AdsRSHBVH6jfy3q2VoGTE_s_AUl4zprVRqsk_Ud3OOqFhHJNkubEQSaV1LaHezL385CX2uR-Uwv94yF538rmkMpvrFlzi817tcB1bqulW1k2-2Zjaxdbj2w7hl0Qw9SBMsXXI0kF5n1k37k1b9Jrec3S0YoYbwfZn061ndnto610wogs96hRWXdUlXZJI8vdgfd1-rn4MFUn9VJvrBxds3qfVxXc9tg1s0raYx1IViwb2smtg6aYXf5Xjpb011fUjy0qwa3bZiOIbZZdz1bYMeqJBigyjkdV9i59_BFJgulqoJfmJf4oiX6WV37OS8JnYiSXZ6mtohq_6IhB2Juh91SplmZZBi49_Jxd9I06opotiQUQlrhJcrM17n6WV5gQYsng6zZtilJu2JZb_m_xeqqXrFfR8exybBhFMkM8qXXgQr2Itob504rjJJxzechtQssod3Jouen68c2bbk7foi8U4ajJ97jl87X_ZlnBJlWR8ORg991uInJj3Y2foMtiBiB_JWd513fMyVrMI4k8yrsWwaO414sblxSoV9xhVxB1pejxhY-xpU-4u-JjuuF_qJuYWWvml67mrMo9X9R1tiM2FsMJcjymZRr5azjJe3II6Vn1mZMQviJvnXQhwp15_OhlaOcnx-R0F4oOxOcsi45_QQQdSkonBtifno47tcFml7iSvRnw3Jv7m8kQm'
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



