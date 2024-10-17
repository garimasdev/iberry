from django.db import models
from django.contrib.auth import get_user_model
from dashboard.models import Room
from accounts.models import User



# notification model for services, room orders, complaints
class Notification(models.Model):
    NOTIFICATION_TYPE = (
        (0, 'Order Placed'),
        (1, 'Report'),
        (2, 'Public'),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    notification_type = models.SmallIntegerField(choices=NOTIFICATION_TYPE, default=0)
    # send_to = models.CharField()
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/notification', blank=True, null=True)
    description = models.CharField(max_length=250, null=True, blank=True)  
    is_readed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class OutdoorNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_readed = models.BooleanField(default=False)



