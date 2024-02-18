from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User

from dashboard.models import Global

@receiver(post_save, sender=User)
def create_user_signal(sender, instance, created, **kwargs):
    if created:
        # Create another object in AnotherModel
        Global.objects.create(user=instance, config_name="room_auth_token_required", config_label="Token Based Access", config_value="N")