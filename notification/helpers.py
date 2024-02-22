from django.conf import settings
import telegram


def telegram_notification(room, channel_name, room_token, request, message_type):
    order_list_url = f'{request.scheme}://{request.get_host()}/dashboard/foors/orders/?token={room_token}'
    message = f'You have received the {message_type} from {room}. View the order list here: \n<a href="{order_list_url}">Click here</a>'
    bot = telegram.Bot(token=settings.TELEGRAM['bot_token'])
    bot.send_message(chat_id=f'@{channel_name}', text=message, parse_mode='html')
