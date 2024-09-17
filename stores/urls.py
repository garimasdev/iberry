from django.urls import path
from accounts.views import UsersViewPage
from . import views
from .views import SearchSuggestionsView
from django.contrib.auth.views import LogoutView
from rest_framework import routers
router = routers.SimpleRouter()
app_name = 'stores'

router.register(r'outdoor-cart', views.OutdoorCartModelView, basename='outdoorcart')
router.register(r'cart', views.CartModelView, basename='cart')
router.register(r'outdoor-order', views.OutdoorOrderView, basename='outdoororder')
router.register(r'order', views.OrderModelView, basename='order')
router.register(r'service-cart', views.ServiceCartModelView, basename='service-cart')
router.register(r'service-order', views.ServiceOrderModelView, basename='service-order')

urlpatterns = [

    # outdoor orders
    path('store/<str:room_token>/foods/outdoor_items/', views.OutdoorHomeViewPage.as_view(), name="foods-outdoor-items"),
    path('outdoor-order/', views.OutdoorOrderModelView.as_view(), name='outdoor_order'),
    # outdoor cart unique id
    path('outdoor_cart/user_id', views.OutdoorCartUserid, name="outdoor_cart_user_id"),
    path('outdoor_order_status/<str:room_token>/<str:order_id>/', views.OutdoorOrderStatusViewPage.as_view(), name="outdoor_order_status"),
    

    # Food 
    path('store/<str:room_token>/', views.ModulesViewPage.as_view(), name="my_url"),
    path('store/<str:room_token>/foods/', views.FoodsPageView.as_view(), name="foods"),
    path('store/<str:room_token>/foods/items/', views.HomeViewPage.as_view(), name="foods-items"),
    path('store/<str:room_token>/foods/bar/', views.BarPageView.as_view(), name="foods-bar"),
    path('store/<str:room_token>/foods/<str:item_id>/', views.ProductDetailView.as_view(), name='food-item-view'),

    # search food items
    path('search/suggestions/', SearchSuggestionsView, name='search-suggestions'),
    

    # Payment urls
    path('payment/checkout/success', views.paymentCheckoutSuccess, name='paymentCheckoutSuccess'),
    path('payment/checkout', views.paymentCheckout, name='payment_checkout'),
    path('create/payment/order', views.CreatePaymentOrder, name='create_payment_order'),
    
    # push notification
    path('firebase-messaging-sw.js',views.showFirebaseJS,name="show_firebase_js"),

    
    # QR code
    path('store/<str:room_token>/hotel-intercom/', views.QRCodeViewPage.as_view(), name="qr-code"),
    
    # complaint 
    path('store/<str:room_token>/complain/', views.ComplainCreateView.as_view(), name="complain"),
    path('store/<str:room_token>/complain/<str:complain_id>/', views.ComplainDetailsView.as_view(), name='complaint_detail'),
    
    
    # path('order/', views.PlaceOrderAPIView.as_view(), name="place-order"),
    path('order/', views.PlaceOrderAPIView, name="place-order"),
    path('order_status/<str:room_token>/<str:order_id>/', views.OrderStatusViewPage.as_view(), name="order_status"),
    
    
    # # room paths
    # path('room/list/', views.RoomViewPage.as_view(), name="room-list"),
    
    #Service
    path('store/<str:room_token>/services/', views.ServicesPageView.as_view(), name="services"),
    path('service-order/', views.ServiceOrderPlaceAPIView.as_view(), name="service-order-place"),
    path('service_order_status/<str:room_token>/<str:order_id>/', views.ServiceOrderStatusViewPage.as_view(), name="order_status"),
    path('configuration/global', views.GlobalUpdateAPIView, name='global-update'),
    path('check/store/<room_token>/config', views.CheckConfigStoreToken, name='check-config-store'),
    path('validate/store/<room_token>/config', views.ValidateConfigStoreToken.as_view(), name='validate-config-store'),


    # STATIC PAGES 
    path('contact-us/', views.contact_us, name='contact_us'),
    path('contact/send', views.contact_send, name='contact_send'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('cancel-refund-policy/', views.cancel_refund, name='cancel_refund'),

    # logo 
    path('company-logo/', views.render_logo, name='display_logo'),

]+ router.urls
