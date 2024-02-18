import re

from dashboard.models import Room
from notification.models import Notification
from notification.serializers import NotificationSerializer
from stores.models import Cart, ServiceCart


def cart_count(request):
    # room_token = request.path.split('/')[-2]
    numbers = re.findall(r"\d+", request.path)
    if numbers:
        try:
            room = Room.objects.get(room_token=numbers[0])
        except Room.DoesNotExist:
            room = None

        if room is not None:
            if request.path == f"/store/{numbers[0]}/services/":
                cart_count = ServiceCart.objects.filter(room=room).count()
            else:
                cart_items = Cart.objects.filter(room=room)
                cart_count = sum(item.quantity for item in cart_items)
        else:
            cart_count = 0
        return {"cart_count": cart_count, "room_number": numbers[0]}
    else:
        return {"cart_count": 0, "room_number": 0}


def notification_count(request):
    if request.user.is_authenticated:
        try:
            notification = Notification.objects.filter(
                room__user=request.user, is_readed=False
            )[:5]
            notification_count = notification.count()
            notification_data = NotificationSerializer(notification, many=True).data
        except Notification.DoesNotExist:
            notification_count = 0

        return {
            "notification_count": notification_count,
            "notifications": notification_data,
        }
    else:
        return {"notification_count": 0, "notifications": []}
