from django.urls import path, re_path
# import reporting
from accounts.views import UsersViewPage
from . import views
from django.contrib.auth.views import LogoutView
from rest_framework import routers
router = routers.SimpleRouter()
# reporting.autodiscover()
app_name = 'dashboard'

router.register(r'food/price', views.FoodPriceModelView, basename='food-price')
urlpatterns = [
    path('', views.DashboardViewPage.as_view(), name="dashboard"),
    path('user/change_password/', views.UserChangePassword, name="user-change-password"),
    path('save/token',views.savetoken, name="fcm-token"),
    # room paths
    path('room/list/', views.RoomViewPage.as_view(), name="room-list"),
    path('room/add/', views.RoomCreateView.as_view(), name="room-add"),
    path('room/update/<int:pk>/', views.RoomUpdateView.as_view(), name="room-update"),
    path('room/update/status/<int:pk>/', views.RoomUpdateAPIView.as_view(), name="room-status-update"),
    path('room/delete/<int:pk>/', views.RoomDeleteAPIView.as_view(), name="room-delete"),
    path('room/send-sms/', views.SendSMSAPIView.as_view(), name="room-send-sms"),
    
    #foods paths
    path('foods/items/', views.FoodsItemsViewPage.as_view(), name="foods-items"),
    path('foods/item/add/', views.FoodsItemCreateView.as_view(), name="foods-item-add"),
    path('foods/item/update/<int:pk>/', views.FoodsItemUpdateView.as_view(), name="foods-item-edit"),
    path('foods/item/delete/<int:pk>/', views.FoodsItemDeleteView.as_view(), name="foods-item-delete"),
    
    path('foods/categories/', views.FoodsCategoriesViewPage.as_view(), name="foods-categories"),
    path('foods/category/add/', views.FoodsCategoryCreateView.as_view(), name="foods-category-add"),
    path('foods/category/update/<int:pk>/', views.FoodsCategoryUpdateView.as_view(), name="foods-category-update"),
    path('foods/category/delete/<int:pk>/', views.FoodsCategoryDeleteView.as_view(), name="foods-category-delete"),
    #Sub Category
    path('foods/categories/sub-categories/', views.FoodsSubCategoriesViewPage.as_view(), name="foods-sub-categories"),
    path('foods/category/sub-category/add/', views.FoodsSubCategoryCreateView.as_view(), name="foods-sub-category-add"),
    path('foods/category/sub-category/update/<int:pk>/', views.FoodsSubCategoryUpdateView.as_view(), name="foods-sub-category-update"),
    path('foods/category/sub-category/delete/<int:pk>/', views.FoodsSubCategoryDeleteView.as_view(), name="foods-sub-category-delete"),
    path('foods/get_subcategories/', views.SubcategoryView.as_view(), name='get_subcategories'),
    
    path('foods/outdoor-orders/', views.FoodsOutdoorOrdersViewPage.as_view(), name="foods-outdoor-orders"),
    path('foods/outdoor-orders/<int:pk>/', views.OutdoorOrderExportPageView.as_view(), name="foods-outdoor-orders-print"),
    path('foors/orders/', views.FoodsOrdersViewPage.as_view(), name="foods-orders"),
    path('foors/orders/<int:pk>/', views.OrderExportPageView.as_view(), name="foods-orders-print"),
    # /dashboard/foods/category/add
    
    
    # Services Path
    path('services/', views.ServiceViewPage.as_view(), name="services"),
    path('services/add/', views.ServiceCreateView.as_view(), name="services-add"),
    path('services/update/<int:pk>/', views.ServiceUpdateView.as_view(), name="services-update"),
    path('services/delete/<int:pk>/', views.ServiceDeleteAPIView.as_view(), name="services-delete"),
    
    #Service Order
    path('services/orders/', views.ServiceOrdersViewPage.as_view(), name="services-orders"),
    
    
    #Complaints Path
    path('complaints/', views.ComplaintsViewPage.as_view(), name="complaints"),
    path('complaints/update/<int:pk>/', views.ComplaintsUpdateAPIView.as_view(), name="complaints-update"),
    path('complaints/delete/<int:pk>/', views.ComplaintsDeleteAPIView.as_view(), name="complaints-delete"),
    
    path('complaints/types/', views.ComplainTypesViewPage.as_view(), name="complaints-types"),
    path('complaints/types/add/', views.ComplainTypeCreateView.as_view(), name="complaint-type-add"),
    path('complaints/types/update/<int:pk>/', views.ComplainTypeUpdateView.as_view(), name="complaint-type-update"),
    path('complaints/types/delete/<int:pk>/', views.ComplainTypeDeleteAPIView.as_view(), name="complaint-type-delete"),
    
    
    #Dialer Path
    path('dialer/', views.DialerViewPage.as_view(), name="dialer-list"),
    path('dialer/add/', views.DialerCreateView.as_view(), name="dialer-add"),
    path('dialer/update/<int:pk>/', views.DialerUpdateView.as_view(), name="dialer-update"),
    path('dialer/delete/<int:pk>/', views.DialerDeleteAPIView.as_view(), name="dialer-delete"),
    
    # Users
    path('users/', UsersViewPage.as_view(), name="user-list"),
    
    path('extension/', views.ExtensionViewPage.as_view(), name="extension-list"),
    path('extension/add/', views.ExtensionCreateView.as_view(), name="extension-add"),
    path('extension/update/<int:pk>/', views.ExtensionUpdateView.as_view(), name="extension-update"),
    path('extension/delete/<int:pk>/', views.ExtensionDeleteAPIView.as_view(), name="extension-delete"),
    
    
    #configurations paths
    path('configuration/pbx/', views.PbxViewPage.as_view(), name="pbx-list"),
    path('configuration/pbx/add/', views.PbxCreateView.as_view(), name="pbx-add"),
    path('configuration/pbx/update/<int:pk>/', views.PbxUpdateView.as_view(), name="pbx-update"),
    path('configuration/pbx/delete/<int:pk>/', views.PbxDeleteView.as_view(), name="pbx-delete"),
    
    path('configuration/janus/', views.JanusViewPage.as_view(), name="janus-list"),
    path('configuration/janus/add/', views.JanusCreateView.as_view(), name="janus-add"),
    path('configuration/janus/update/<int:pk>/', views.JanusUpdateView.as_view(), name="janus-update"),
    path('configuration/janus/delete/<int:pk>/', views.JanusDeleteView.as_view(), name="janus-delete"),
    
    path('configuration/global/', views.GlobalViewPage.as_view(), name="global-list"),
    # path('configuration/global/<pk>/', views.GlobalUpdateAPIView, name='global-update'),
    
    #Report Order
    path('reports/', views.OrderReportView.as_view(), name='order_report'),
    # path('report/', OrderReport, name='report'),

    # re_path(r'^.*\.*', views.pages, name='pages'),
]+ router.urls
