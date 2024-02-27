from django.conf import settings
import telegram


# telegram channel notification for all platforms
def telegram_notification(channel_name, message):
    bot = telegram.Bot(token=settings.TELEGRAM['bot_token'])
    bot.send_message(chat_id=f'@{channel_name}', text=message, parse_mode='html')
