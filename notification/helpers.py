import traceback
from django.conf import settings
import telegram
from telegram import ParseMode
import traceback


# telegram channel notification for all platforms
def telegram_notification(channel_name, bot_token, message):
    try:
        # bot = telegram.Bot(token=settings.TELEGRAM['bot_token'])
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=f'@{channel_name}', text=message,  parse_mode=ParseMode.HTML)
    except:
        traceback.print_exc()
