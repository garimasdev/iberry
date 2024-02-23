from django.urls import path, re_path

from accounts.views import UsersViewPage
from . import views
from django.contrib.auth.views import LogoutView
from rest_framework import routers
router = routers.SimpleRouter()
app_name = 'stores'

router.register(r'outdoor-cart', views.OutdoorCartModelView, basename='outdoorcart')
router.register(r'cart', views.CartModelView, basename='cart')
# router.register(r'outdoor-order', views.OutdoorOrderModelView, basename='outdoororder')
router.register(r'order', views.OrderModelView, basename='order')
router.register(r'service-cart', views.ServiceCartModelView, basename='service-cart')
router.register(r'service-order', views.ServiceOrderModelView, basename='service-order')

urlpatterns = [
    path('firebase-messaging-sw.js',views.showFirebaseJS,name="show_firebase_js"),
    path('outdoor-order/', views.OutdoorOrderModelView.as_view(), name='outdoororder'),
    path('store/<str:room_token>/', views.ModulesViewPage.as_view(), name="my_url"),
    path('store/<str:room_token>/foods/', views.FoodsPageView.as_view(), name="foods"),
    path('store/<str:room_token>/foods/outdoor_items/', views.OutdoorHomeViewPage.as_view(), name="foods-outdoor-items"),
    path('store/<str:room_token>/foods/items/', views.HomeViewPage.as_view(), name="foods-items"),
    path('store/<str:room_token>/foods/bar/', views.BarPageView.as_view(), name="foods-bar"),
    path('store/<str:room_token>/foods/<str:item_id>/', views.ProductDetailView.as_view(), name='food-item-view'),
    
    path('store/<str:room_token>/hotel-intercom/', views.QRCodeViewPage.as_view(), name="qr-code"),
    
    path('store/<str:room_token>/services/', views.ServicesPageView.as_view(), name="services"),
    
    path('store/<str:room_token>/complain/', views.ComplainCreateView.as_view(), name="complain"),
    path('store/<str:room_token>/complain/<str:complain_id>/', views.ComplainDetailsView.as_view(), name='complaint_detail'),
    
    
    # path('order/', views.PlaceOrderAPIView.as_view(), name="place-order"),
    path('order/', views.PlaceOrderAPIView, name="place-order"),
    path('order_status/<str:room_token>/<str:order_id>/', views.OrderStatusViewPage.as_view(), name="order_status"),
    
    # # room paths
    # path('room/list/', views.RoomViewPage.as_view(), name="room-list"),
    
    #Service
    path('service-order/', views.ServiceOrderPlaceAPIView.as_view(), name="service-order-place"),
    path('service_order_status/<str:room_token>/<str:order_id>/', views.ServiceOrderStatusViewPage.as_view(), name="order_status"),
    
]+ router.urls
