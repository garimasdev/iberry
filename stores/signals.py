from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from dashboard.models import Complain, Global
from notification.models import Notification
from stores.models import Order, ServiceOrder
import uuid

@receiver(post_save, sender=Order)
def order_place(sender, instance, created, **kwargs):
    if instance.status == 2:
        for get_item in instance.items.all():
            item = get_item.item
            item.quantity -= get_item.quantity
            item.save()
        
    if created:
        # Create another object in AnotherModel
        Notification.objects.create(room=instance.room, title=f"From room {instance.room.room_number} an order has been placed.")
        

@receiver(pre_save, sender=Complain)
def create_complain(sender, instance, **kwargs):
    if not instance.complain_id:
        instance.complain_id =  str(uuid.uuid4().int & (10**8-1))
        # Create another object in AnotherModel
        # Notification.objects.create(room=instance.room, title=f"From room {instance.room.room_number} an order has been placed.")
        
@receiver(post_save, sender=Complain)
def created_complain(sender, instance, created, **kwargs):    
    if created:
        # Create another object in AnotherModel
        Notification.objects.create(room=instance.room, title=f"From room {instance.room.room_number} a complain has been placed.")


@receiver(post_save, sender=ServiceOrder)
def service_order_place(sender, instance, created, **kwargs):    
    if created:
        # Create another object in AnotherModel
        Notification.objects.create(room=instance.room, title=f"From room {instance.room.room_number} an order has been placed.")