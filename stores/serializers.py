import uuid
from django.contrib.auth import get_user_model
from dashboard.models import Service
from dashboard.serializers import FoodItemsSerializer, OrderRoomSerializer, PriceSerializer
from rest_framework import serializers
from stores.models import Cart, Item, Order, OrderItem, ServiceCart, ServiceOrder
from django.utils import dateparse
                

"""
    Configuration Serializers
"""

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    item = FoodItemsSerializer()
    class Meta:
        model = Cart
        fields = '__all__'
        



class OrderItemSerializer(serializers.ModelSerializer):
    # product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ('item', 'quantity')

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than zero.')
        return value

class CustomOrderSerializer(serializers.Serializer):
    room = serializers.IntegerField()
    
    
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.HiddenField(default=0)
    
    class Meta:
        model = Order
        fields = ('order_id', 'room', 'items', 'total_price')
 
 
class ItemSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=True)   
    
    class Meta:
        model = Item
        fields = '__all__'
           

class UpdateOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = ['status', 'note']
        

"""
Service cart
"""
class ServiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['image', 'name', 'price']
        
        
class GetServiceCartSerializer(serializers.ModelSerializer):
    service = ServiceListSerializer()
    class Meta:
        model = ServiceCart
        fields = '__all__'
        

class ServiceCartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceCart
        fields = '__all__'
        

class ServiceOrderSerializer(serializers.ModelSerializer):
    # services = OrderItemSerializer(many=True)
    total_price = serializers.HiddenField(default=0)
    
    class Meta:
        model = ServiceOrder
        fields = ('order_id', 'room', 'services', 'total_price')
        

class ServiceUpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrder
        fields = ['status', 'note']        

class ServiceOrdersSerializer(serializers.ModelSerializer):
    STATUS = (
        (0, "Ordered"),
        (1, "Processing"),
        (2, "Completed"),
        (3, "Canceled"),
    )
    
    room = OrderRoomSerializer()
    # services = GetServiceCartSerializer(many=True, read_only=True)
    status = serializers.ChoiceField(choices=STATUS, source='get_status_display')
    created_at = serializers.SerializerMethodField(read_only=True)
    
    def get_created_at(self, obj) -> str:
        return dateparse.parse_datetime(str(obj.created_at))
    
    class Meta:
        model = ServiceOrder
        fields = '__all__'