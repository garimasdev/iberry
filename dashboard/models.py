from urllib import request
import uuid
from django.db import models
from accounts.models import User
from dashboard.utils import generateAuthToken
from datetime import datetime


# Create your models here.
class Pbx(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pbx_name = models.CharField(max_length=100)
    pbx_domain = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
       ordering = ['-created_at']
       
    
    @staticmethod
    def has_read_permission(request):
        return False
       
    def has_object_read_permission(self, request):
        return request.user == self.user
    
    @staticmethod
    def has_write_permission(request):
        return False
    
    
    def has_object_write_permission(self, request):
        return request.user == self.user
    
    def __str__(self):
        return f"{self.pbx_name}"
       
       
class Janus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    janus_name = models.CharField(max_length=100)
    janus_domain = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
       ordering = ['-created_at']
       
    
    @staticmethod
    def has_read_permission(request, self):
        return request.user == self.user
       
    def has_object_read_permission(self, request):
        return request.user == self.user
    
    @staticmethod
    def has_write_permission(request, self):
        return request.user == self.user
    
    
    def has_object_write_permission(self, request):
        return request.user == self.user
    
    def __str__(self):
        return f"{self.janus_name}"
    
    
class Extension(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    extension_name = models.CharField(max_length=100)
    extension_sip_number = models.CharField(max_length=100)
    extension_sip_password = models.CharField(max_length=100)
    pbx = models.ForeignKey(Pbx, on_delete=models.CASCADE)
    janus = models.ForeignKey(Janus, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
       ordering = ['-created_at']
       
       
    @staticmethod
    def has_read_permission(request, self):
        return request.user == self.user
       
    def has_object_read_permission(self, request):
        return request.user == self.user
    
    @staticmethod
    def has_write_permission(request, self):
        return request.user == self.user
    
    
    def has_object_write_permission(self, request):
        return request.user == self.user
       
    def __str__(self):
        return f"{self.extension_name}"


class Global(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    config_name = models.CharField(max_length=100)
    config_value = models.CharField(max_length=150, null=True, blank=True)
    config_label = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
       ordering = ['-created_at']
    
    
    @staticmethod
    def has_read_permission(request, self):
        return request.user == self.user
       
    def has_object_read_permission(self, request):
        return request.user == self.user
    
    @staticmethod
    def has_write_permission(request, self):
        return request.user == self.user
    
    
    def has_object_write_permission(self, request):
        return request.user == self.user
       
    def __str__(self):
        return f"{self.config_name}"
    


class Dialer(models.Model):
    extension = models.ForeignKey(Extension, on_delete=models.CASCADE)
    c2c_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
       ordering = ['-created_at']
       
       
    def __str__(self):
        return f"{self.c2c_name}"
    
    
class Room(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_number	= models.IntegerField()
    extension = models.ForeignKey(Extension, on_delete=models.CASCADE)
    room_token = models.CharField(max_length=50, null=True, blank=True)
    short_url = models.CharField(max_length=150, null=True, blank=True)
    auth_token = models.CharField(max_length=150, null=True, blank=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
       ordering = ['-created_at']
       
    def __str__(self):
        return f"{self.room_number}"
    
    
    def save(self, *args, **kwargs):
        created = not self.pk
        if created:
            self.room_token = str(uuid.uuid4().int & (10**8-1))
            # short_url_generate = getShortUrl(self.room_token)
            self.short_url = "https://iberry.caucasianbarrels.com/store/"+self.room_token+"/"
            # "https://curt.shop/?"+short_url_generate['token']
            self.auth_token = generateAuthToken()
            
        super().save(*args, **kwargs) 
       

class Service(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/services/')
    name = models.CharField(max_length=150)
    price = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.name}"


    
class ComplainType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title}"
    
    
class Complain(models.Model):
    STATUS = (
        (0, "Complained"),
        (1, "Processing"),
        (2, "Completed"),
        (3, "Canceled"),
    )
    
    complain_placed_id = models.CharField(max_length=8, unique=True, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    complain = models.ForeignKey(ComplainType, on_delete=models.CASCADE)
    report = models.TextField()
    status = models.SmallIntegerField(choices=STATUS, default=0, null=True, blank=True)
    note = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
           ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.complain.title}"
    
    
    def save(self, *args, **kwargs):
        # Update the updated_at field when the status changes
        if self.pk is not None:
            original_instance = Complain.objects.get(pk=self.pk)
            if original_instance.status != self.status:
                self.updated_at = datetime.now()

        super(Complain, self).save(*args, **kwargs)
    