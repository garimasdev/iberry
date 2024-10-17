from rest_framework import serializers
from push_notifications.api.rest_framework import DeviceSerializerMixin, UniqueRegistrationSerializerMixin, \
    HexIntegerField, ValidationError, UNSIGNED_64BIT_INT_MAX_VALUE, hex_re
from push_notifications.models import GCMDevice
from django.contrib.auth import get_user_model
from notification.models import Notification, OutdoorNotification

class GCMDeviceSerializer(UniqueRegistrationSerializerMixin, serializers.ModelSerializer):
    device_id = HexIntegerField(
        help_text="ANDROID_ID / TelephonyManager.getDeviceId() (e.g: 0x01)",
        style={"input_type": "text"},
        required=False,
        allow_null=True
    )

    class Meta(DeviceSerializerMixin.Meta):
        model = GCMDevice
        fields = (
            "id", "name", "registration_id", "device_id", "active", "date_created",
            "cloud_message_type"
        )
        extra_kwargs = {"id": {"read_only": True}}

    def validate_device_id(self, value):
        # device ids are 64 bit unsigned values
        if value > UNSIGNED_64BIT_INT_MAX_VALUE:
            raise ValidationError("Device ID is out of range")
        return value
    
class NotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notification
        fields = '__all__'
        # exclude = ['content']


class OutdoorNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutdoorNotification
        fields = '__all__'
        