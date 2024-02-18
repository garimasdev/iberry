from rest_framework import serializers
from accounts.models import User


"""
    Room Serializers
"""
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'