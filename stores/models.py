from datetime import datetime
from django.db import models
# from django.contrib.auth.models import User
from accounts.models import User
from dashboard.models import Room, Service

# Create your models here.
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, db_index=True)
    
    class Meta:
        unique_together = ('user', 'name')
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name;



class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, db_index=True)
    
    class Meta:
        unique_together = ('category', 'name')
        verbose_name_plural = 'sub categories'
    
    def __str__(self):
        return self.name;
    


class Price(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    sell_price = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}-{self.price}"
    

class Item(models.Model):
    TYPES = (
        ("None", "None"),
        ("Veg", "Veg"),
        ("Non Veg", "Non Veg")
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='Item', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    # images = models.ManyToManyField('Image')
    image = models.ImageField(upload_to='foods/items/')
    prices = models.ManyToManyField(Price)
    quantity = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    item_type = models.CharField(max_length=20, choices=TYPES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
    class Meta:
        verbose_name_plural = 'Items'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.user.username + "  " + self.category.name
        

class Image(models.Model):
    file = models.ImageField(upload_to='items/')


class Temporary_Users(models.Model):
    anonymous_user_id = models.CharField(max_length=80, null=True, blank=True, unique=True)
    custom_order_id = models.CharField(max_length=80, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=80, null=True, blank=True)
    receipt = models.CharField(max_length=16, null=True, blank=True)
    order_total = models.CharField(max_length=60, null=True, blank=True)
    customer_name = models.CharField(max_length=60, null=True, blank=True)
    customer_email = models.CharField(max_length=60, null=True, blank=True)
    customer_phone = models.CharField(max_length=60, null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'temp_users'

class OutdoorCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    anonymous_user_id = models.CharField(max_length=80, null=True, blank=True)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
  
    def placeOrder(self):
        self.save()
  
    @staticmethod
    def get_orders_by_customer(user):
        return OutdoorCart.objects.filter(user=user).order_by('-created_at')
    
    class Meta:
        unique_together = ('user', 'item')
        ordering = ['-created_at']


class Cart(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
  
    def placeOrder(self):
        self.save()
  
    @staticmethod
    def get_orders_by_customer(user):
        return Cart.objects.filter(user=user).order_by('-created_at')
    
    
    class Meta:
        unique_together = ('room', 'item')
        ordering = ['-created_at']
        
        

class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='order_items')
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    price = models.IntegerField(editable=False)
    quantity = models.PositiveSmallIntegerField()
    

class OutdoorOrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='outdoor_order_items')
    order = models.ForeignKey('OutdoorOrder', on_delete=models.CASCADE)
    price = models.IntegerField(editable=False)
    quantity = models.PositiveSmallIntegerField()


class Order(models.Model):
    STATUS = (
        (0, "Ordered"),
        (1, "Processing"),
        (2, "Completed"),
        (3, "Canceled"),
    )
    order_id = models.CharField(max_length=8, unique=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem, related_name='stores_order_items')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.SmallIntegerField(choices=STATUS, default=0)
    note = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @staticmethod
    def has_read_permission(request):
        return True
    
    @staticmethod
    def has_write_permission(request):
        return True
    
    class Meta:
        ordering = ['-created_at']
        
        
    def save(self, *args, **kwargs):
        # Update the updated_at field when the status changes
        if self.pk is not None:
            original_instance = Order.objects.get(pk=self.pk)
            if original_instance.status != self.status:
                self.updated_at = datetime.now()

        super(Order, self).save(*args, **kwargs)


class OutdoorOrder(models.Model):
    STATUS = (
        (0, "Ordered"),
        (1, "Processing"),
        (2, "Completed"),
        (3, "Canceled"),
    )
    order_id = models.CharField(max_length=8, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OutdoorOrderItem, related_name='stores_outdoor_order_items')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.SmallIntegerField(choices=STATUS, default=0)
    note = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @staticmethod
    def has_read_permission(request):
        return True
    
    @staticmethod
    def has_write_permission(request):
        return True
    
    class Meta:
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        # Update the updated_at field when the status changes
        if self.pk is not None:
            original_instance = OutdoorOrder.objects.get(pk=self.pk)
            if original_instance.status != self.status:
                self.updated_at = datetime.now()

        super(OutdoorOrder, self).save(*args, **kwargs)



"""
Service cart Model
"""
class ServiceCart(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
  
    def placeOrder(self):
        self.save()
  
    @staticmethod
    def get_orders_by_customer(user):
        return ServiceCart.objects.filter(user=user).order_by('-created_at')
    
    
    class Meta:
        unique_together = ('room', 'service')
        ordering = ['-created_at']
        

class ServiceOrderItem(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='order_service')
    order = models.ForeignKey('ServiceOrder', on_delete=models.CASCADE)
    price = models.IntegerField(editable=False)
    quantity = models.PositiveSmallIntegerField()

    
class ServiceOrder(models.Model):
    STATUS = (
        (0, "Ordered"),
        (1, "Processing"),
        (2, "Completed"),
        (3, "Canceled"),
    )
    order_id = models.CharField(max_length=8, unique=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    services = models.ManyToManyField(ServiceOrderItem, related_name='stores_order_services')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.SmallIntegerField(choices=STATUS, default=0)
    note = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
              
    def save(self, *args, **kwargs):
        # Update the updated_at field when the status changes
        if self.pk is not None:
            original_instance = ServiceOrder.objects.get(pk=self.pk)
            if original_instance.status != self.status:
                self.updated_at = datetime.now()

        super(ServiceOrder, self).save(*args, **kwargs)