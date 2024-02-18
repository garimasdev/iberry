from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from notification.models import Notification
from push_notifications.models import GCMDevice

# @receiver(post_save, sender=Notification)
def send_push_notifications(instance, created, *args, **kargs):

    if not created:
        return
    fcm_devices = GCMDevice.objects.filter(cloud_message_type="FCM")
    if not fcm_devices:
        return
    
    extra = {
        'title': instance.title,
        'body': instance.description,
        'notification_type': 'Reports',
        'room': instance.room.id,
        'object_id': instance.id,
    }
    fcm_devices.send_message(instance.title, extra=extra)
    
# @receiver(pre_save, sender=Notification)
# def send_push_notifications(instance, *args, **kargs):
#     pass
#     # fcm_devices = GCMDevice.objects.filter(cloud_message_type="FCM")
#     # if not fcm_devices:
#     #     return
#     # extra = {
#     #     'notification_type': 'Reports',
#     #     'from_user': '',
#     #     'object_id': instance.id,
#     # }
#     # fcm_devices.send_message(instance.title, extra=extra)