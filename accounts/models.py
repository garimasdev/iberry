from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class UserManager(BaseUserManager):
    def _create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('UID number must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.outdoor_token = str(uuid.uuid4().int & (10**8-1))
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)


        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    
    
class User(AbstractUser):
    """
    Extends the Django's AbstractUser to create a customizable User model.
    """
    GENDER_CHOICES = (
        ('m', 'male'),
        ('f', 'female'),
    )
    
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text=_('150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    phone = models.CharField(_("phone number"), max_length=15, unique=True, null=True, blank=True)
    picture = models.ImageField(upload_to='profile_pictures', null=True, blank=True)
    otp = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    second_address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    postal_code = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    firebase_token = models.TextField(null=True, blank=True)
    channel_name = models.CharField(max_length=70, null=True, blank=True)
    outdoor_token = models.CharField(max_length=20, null=True, blank=True)
    # phonepe configuration
    razorpay_clientid = models.CharField(max_length=255, null=True, blank=True)
    razorpay_clientsecret = models.CharField(max_length=255, null=True, blank=True)
    # GST details fields
    gst_number = models.CharField(max_length=15, null=True, blank=True, unique=True)


    USERNAME_FIELD = 'username'
    objects = UserManager()
    
    class Meta:
       ordering = ['-created_at']

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_write_permission(self, request):
        return request.user == self

    def __str__(self):
        return f"{self.name}"
    

