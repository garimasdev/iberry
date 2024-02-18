import uuid
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from django.utils import dateparse
from dashboard.models import Complain, ComplainType, Dialer, Extension, Global, Janus, Pbx, Room, Service
from stores.models import Category, Item, Order, OrderItem, Price, ServiceOrder, ServiceOrderItem, SubCategory
                

"""
    Configuration Serializers
"""

class PbxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pbx
        fields = '__all__'


class PbxNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pbx
        fields = ['pbx_name', 'pbx_domain']
        

class JanusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Janus
        fields = '__all__'


class JanusNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Janus
        fields = ['janus_name', 'janus_domain']
        
                

class GlobalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Global
        fields = '__all__'
        
class GlobalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Global
        fields = ['config_value']
        


"""
    Extension Serializers
"""

class ExtensionSerializer(serializers.ModelSerializer):
    pbx = PbxNameSerializer()
    janus = JanusNameSerializer()
    class Meta:
        model = Extension
        fields = '__all__'
        
        
                

"""
    Room Serializers
"""
class RoomSerializer(serializers.ModelSerializer):
    extension = ExtensionSerializer()
    class Meta:
        model = Room
        fields = '__all__'


class OrderRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['room_number']
        
        

class RoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['status']
        

"""
   Foods Category
"""
class FoodCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

        

class FoodCategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name',]
        


class FoodSubCategoriesSerializer(serializers.ModelSerializer):
    category = FoodCategoryNameSerializer()
    class Meta:
        model = SubCategory
        fields = '__all__'
        

class SubCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['name']
        
        
"""
    Foods Serializers
"""

class PriceSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault());
    class Meta:
        model = Price
        fields = '__all__'

class FoodItemAPISerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Item
        fields = '__all__'
                

class FoodItemsSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField(read_only=True)
    category = FoodCategoryNameSerializer()
    sub_category = SubCategoriesSerializer()
    prices = PriceSerializer(many=True)
    
    def get_created_at(self, obj) -> str:
        return dateparse.parse_datetime(str(obj.created_at))
    
    class Meta:
        model = Item
        fields = '__all__'


# class FoodOrderItemsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    item = FoodItemsSerializer()

    class Meta:
        model = OrderItem
        fields = '__all__'  # Specify the fields you want to include

                

class FoodOrdersSerializer(serializers.ModelSerializer):
    STATUS = (
        (0, "Ordered"),
        (1, "Processing"),
        (2, "Completed"),
        (3, "Canceled"),
    )
    
    room = OrderRoomSerializer()
    items = OrderItemSerializer(many=True, read_only=True)
    status = serializers.ChoiceField(choices=STATUS, source='get_status_display')
    created_at = serializers.SerializerMethodField(read_only=True)
    
    def get_created_at(self, obj) -> str:
        return dateparse.parse_datetime(str(obj.created_at))
    
    class Meta:
        model = Order
        fields = '__all__'



"""
    Dialer Serializers
"""
class DialerSerializer(serializers.ModelSerializer):
    extension = ExtensionSerializer()
    class Meta:
        model = Dialer
        fields = '__all__'
        

class PhoneDialerSerializer(serializers.ModelSerializer):
    extension = ExtensionSerializer()
    class Meta:
        model = Dialer
        fields = '__all__'
        

class ServiceSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Service
        fields = '__all__'
        


class ServiceNameSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Service
        fields = ['name']
        

class ServiceItemSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Service
        fields = ['name', 'image', 'price']
        

class OrderedServiceItemSerializer(serializers.ModelSerializer):
    service = ServiceItemSerializer()
    
    class Meta:
        model = ServiceOrderItem
        fields = '__all__'


class ServiceOrdersSerializer(serializers.ModelSerializer):
    STATUS = (
        (0, "Ordered"),
        (1, "Processing"),
        (2, "Completed"),
        (3, "Canceled"),
    )
    
    room = OrderRoomSerializer()
    services = OrderedServiceItemSerializer(many=True)
    status = serializers.ChoiceField(choices=STATUS, source='get_status_display')
    created_at = serializers.SerializerMethodField(read_only=True)
    
    def get_created_at(self, obj) -> str:
        return dateparse.parse_datetime(str(obj.created_at))
    
    class Meta:
        model = ServiceOrder
        fields = '__all__'

        
class ComplainTypeTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplainType
        fields = ['title']
        
        
class ComplainSerializer(serializers.ModelSerializer):
    STATUS = (
        (0, "Complained"),
        (1, "Processing"),
        (2, "Completed"),
        (3, "Canceled"),
    )
    complain = ComplainTypeTitleSerializer()
    room = OrderRoomSerializer()
    status = serializers.ChoiceField(choices=STATUS, source='get_status_display')
    
    
    class Meta:
        model = Complain
        fields = '__all__'
        


class ComplainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplainType
        fields = '__all__'


class UpdateComplainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complain
        fields = ['status', 'note']
        
