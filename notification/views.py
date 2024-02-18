from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from push_notifications.models import APNSDevice, GCMDevice
from push_notifications.api.rest_framework import DeviceViewSetMixin, AuthorizedMixin
from rest_framework import viewsets, generics, status
from dashboard.views import UserAccessMixin
from notification.forms import NotificationForm
from notification.models import Notification
from notification.serializers import GCMDeviceSerializer, NotificationSerializer
from django.db.models import Q
# Create your views here.

class GCMDeviceViewset(
    AuthorizedMixin,
    DeviceViewSetMixin, 
    viewsets.ModelViewSet
    ):
    queryset = GCMDevice.objects.all()
    serializer_class = GCMDeviceSerializer
    
class NotificationView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Notification.objects.all()
        else:
            queryset = Notification.objects.filter(notification_type=0)
        return queryset
    

    
# Admin Notification view
class NotificationPageView(UserAccessMixin, ListView):
    permission_required = 'notification.view_notification'
    template_name = 'notification/notification.html'
    model = Notification
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(title__icontains=q) | Q(notification_type__icontains=q)
            )
        else:
            object_list = self.model.objects.all()
        return object_list
    

class NotificationCreateView(UserAccessMixin, CreateView):
    permission_required = 'notification.create_notification'
    model = Notification
    form_class = NotificationForm
    success_url	= '/dashboard/notifications/'
    
class NotificationUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'notification.edit_notification'
    model = Notification
    form_class = NotificationForm
    success_url	= '/dashboard/notifications/'