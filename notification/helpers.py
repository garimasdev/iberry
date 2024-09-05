import traceback
import telegram
from telegram import ParseMode
import traceback
import google.auth
from google.oauth2 import service_account
import google.auth.transport.requests
import requests


# generating a new access token in firebase
def firebase_noti():
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
    access_token = 'ya29.c.c0ASRK0GZKlDXcFfP6KwHmuJkUHqa5dQhuRXWXAKLvd0n8btUWJtueOQBQE09f2zK8mnXBwMBahkNr3zeKMMYWtRxKdZI7SxDC0mu1NaQtbxhN7lPIWfui2P-hu1T-plnvSqD9VxH2sGDXUvuPzK243StamyhODVYC5MPvg4ujUFCNLIFrt8N1-VUYogLR6mIV6n3bMYZ5rgc91T_uRQBKKT9SCMOTsRVxL2ev5_zNjQ06U9LmFcmAW3WVRB33cyjZzN_QN-0dKxpqDma4OQIwpWHlk_JUK8ClSxay7n77IHuDWKlKbMUcETgZhjlppo_tN6un8oYDonbFThbrn_QGjt44v4Iot_goWYKH3sU2J_PqCL4DApM9ig2tN385K9JYc2p-mU_MgxaBlxBaVrcx7bzF-RI6at3t-j7Vqf9o6eSomshM4yW8FutUrX2hn3lY7IcJlvu2FsFpF3_cq4VewQwQRb_bbYur6ZZsIXFZw1meloWpaYwFhmel5SRUrdiy8WjnvF6Qvx_ik4xzkdh2ZVR0Z3bhl10rwpIuileJp3O_f97Snewim8x9B84B-se-nJrXvlrBhMcMucf4ghMwXwRaXWuq7xr2wY3abrkzsiOvohf698JufW05cXSs01Sn_7wjfmI3MF5lq1k0z6dh9Z8mlMWIrpgYnupJqlJBpx9x4sFhozR4BrVhOkXufUZZwfs2MmqMc-sa5wexgQ8qSRb-wrylxi7UMhqYqjQZIdVumivmxud5mnQmFa-y34bSIm-Xo9dM2J_qvM03VsJggjg95FRSBupke-_yeq79udjoyBR-iM5IXF168rt6oJ9b165dVcd8_dzjZM9xVJV4QiIdOZytfg3u8pzXy8x0UgOxS8Fu25_5v-405dVtyt_wubv026rQW7ZeY0j6bsxo-SeW1226b77j0_Bg4q_8_0-JYWtc6-rzbFIOI1jOBdqijW5xWnWw2cfvIyjn7lXkzytF77IoRBb22jV4mYtItsxqheJmJgrJ_1k'
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
        access_token = firebase_noti()
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



