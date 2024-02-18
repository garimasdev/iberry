from django.conf import settings
import telegram


def telegram_notification(room, channel_name):
    message = f"You have received the order from {room}"
    bot = telegram.Bot(token=settings.TELEGRAM['bot_token'])
    bot.send_message(chat_id=f'@{channel_name}', text=message)
