from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.admin import register
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField    
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.forms import UserCreationForm
from accounts.models import User
from import_export import resources
from import_export.admin import ImportExportModelAdmin
#@register(get_user_model())
class UserAdmin(BaseUserAdmin):
    
    add_form = UserCreationForm
    
    fieldsets = (
        (None, {'fields': ('username', 'name')}),
        (_('Personal info'), {'fields': ('email', 'phone', 'picture', 'address', 'channel_name', 'outdoor_token', 'razorpay_clientid', 'razorpay_clientsecret', 'gst_number')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'password1', 'password2', 'channel_name', 'outdoor_token', 'razorpay_clientid', 'razorpay_clientsecret', 'gst_number', 'picture', 'is_staff',
                       'is_superuser'),
        }),
    )
    list_display = ('username', 'name', 'email', 'phone', 'is_superuser', 'channel_name', 'outdoor_token', 'razorpay_clientid', 'razorpay_clientsecret', 'gst_number', 'firebase_token')
    search_fields = ('username', 'email', 'name')
    ordering = ('created_at',)
    # readonly_fields = ('username',)
    filter_horizontal = ()
    list_filter = ('is_staff', 'is_superuser')

    def has_add_permission(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return True
        return False
    
class UserResource(resources.ModelResource):
    class Meta:
        model = get_user_model()
        
class CustomUserAdmin(ImportExportModelAdmin):
   resource_class = UserResource


@admin.register(get_user_model())
class CustomUserAdmin(CustomUserAdmin, UserAdmin):
    pass
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.register(Group)
