from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter

app_name = 'notification'

router = SimpleRouter()
router.register(r'gcm', views.GCMDeviceViewset)

urlpatterns = [
    # path('get-notifications/', views.NotificationView.as_view(), name="notifications"),
] + router.urls