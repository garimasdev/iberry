import re
from accounts.models import User
from dashboard.models import Room
from notification.models import Notification
from notification.serializers import NotificationSerializer
from stores.models import Cart, OutdoorCart, ServiceCart
from django.core.exceptions import ObjectDoesNotExist




def cart_count(request):
    # Define a regex pattern to match the room token
    pattern = r'/store/([^/]+)/'
    token = re.search(pattern, request.path)

    if token:
        # Extract the room token from the matched group
        token = token.group(1)
        
        try:
            # Try to get the room by token
            room = Room.objects.get(room_token=token)
            cart_count = 0
            
            # Check the specific path for services
            if request.path == f"/store/{token}/services/":
                cart_count = ServiceCart.objects.filter(room=room).count()
            else:
                cart_items = Cart.objects.filter(room=room)
                cart_count = sum(item.quantity for item in cart_items)
        
        except Room.DoesNotExist:
            try:
                # If Room does not exist, try to get the User by outdoor_token
                outdoor_token = User.objects.get(outdoor_token=token)
                user_id = request.session.get("user_id")
                
                cart_items = OutdoorCart.objects.filter(user__pk=outdoor_token.pk, cart_user_id=user_id)
                cart_count = sum(item.quantity for item in cart_items)
                
            except ObjectDoesNotExist:
                # Handle case where neither Room nor User exists
                cart_count = 0

        return {"cart_count": cart_count, "room_number": token}
    
    return {"cart_count": 0, "room_number": 0}



def notification_count(request):
    if request.user.is_authenticated:
        try:
            notification = Notification.objects.filter(
                room__user=request.user, is_readed=False
            )
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
