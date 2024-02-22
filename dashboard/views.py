from datetime import datetime
import random
import string
from django.db.models import Count, Q
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, TemplateView, UpdateView, DeleteView, CreateView
from django.contrib.auth.views import LoginView
from accounts.models import User
# from dashboard.serializers import AdmissionsSerializer
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, DestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db.models.functions import TruncDay
from core import settings
from dashboard.forms import ComplainTypeForm, DialerForm, ExtensionForm, FoodsCategoryForm, FoodsItemForm, JanusForm, PbxForm, RoomForm, ServiceForm, SubCategoryForm
from dashboard.models import Complain, ComplainType, Dialer, Extension, Global, Janus, Pbx, Room, Service
from dashboard.serializers import ComplainSerializer, ComplainTypeSerializer, DialerSerializer, ExtensionSerializer, FoodCategoriesSerializer, FoodItemAPISerializer, FoodItemsSerializer, FoodOrdersSerializer, FoodSubCategoriesSerializer, GlobalSerializer, GlobalUpdateSerializer, JanusSerializer, PbxSerializer, PriceSerializer, RoomSerializer, RoomUpdateSerializer, ServiceOrdersSerializer, ServiceSerializer, UpdateComplainSerializer
from urllib.request import urlopen
import json
import urllib
from django.http import HttpResponse
from openpyxl.styles import Alignment
from django.http import JsonResponse
from django.urls import reverse_lazy
from stores.models import Category, Item, Order, Price, ServiceOrder, SubCategory
from django_filters.views import FilterView
from .filters import OrderFilter
import openpyxl
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
class UserAccessMixin(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if (not self.request.user.is_authenticated):
            return redirect('/login/?next=/dashboard/')
        if not self.has_permission():
            return redirect('/');
        return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)
    

class DashboardViewPage(UserAccessMixin, TemplateView):
    # UserAccessMixin,
    permission_required = 'dashboard.view_room'
    template_name = "tabs/dashboard/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_rooms'] = Room.objects.filter(user=self.request.user).count()
        context['total_active_rooms'] = Room.objects.filter(user=self.request.user, status=True).count()
        context['total_in_active_rooms'] = context['total_rooms'] - context['total_active_rooms']
        context['total_extensions'] = Extension.objects.filter(user=self.request.user).count()
        context['total_orders'] = Order.objects.filter(room__user=self.request.user).count()
        context['completed_orders'] = Order.objects.filter(room__user=self.request.user, status=2).count()
        context['ordered_orders'] = Order.objects.filter(Q(room__user=self.request.user) & Q(status=0) | Q(status=1)).count()
        return context
    

@csrf_exempt
def savetoken(request):
    if request.method == 'POST':
        fcm_token = json.loads(request.body).get('fcm_token')
        email = request.user.email
        user = User.objects.get(email=email)
        user.firebase_token = fcm_token
        user.save()
        return JsonResponse("Token saved successfully")



"""
Room page view
"""
class RoomCreateView(UserAccessMixin, CreateView):
    permission_required = 'dashboard.add_room'
    template_name = "tabs/room/room_add.html"
    model = Room
    serializer_class = RoomSerializer
    form_class = RoomForm
    success_url	= '/dashboard/room/list/'
    
    def get_form_kwargs(self):
        kwargs = super(RoomCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class RoomUpdateAPIView(UserAccessMixin, UpdateAPIView):
    permission_required = 'dashboard.change_room'
    queryset = Room.objects.all()
    # serializer_class = RoomUpdateSerializer
    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = request.data.get('status', json.loads(request.body).get('status', False))
        obj.auth_token = ''.join(random.choices(string.ascii_letters+string.digits, k=6))
        obj.save()
        return Response("New token generated")
    

class  RoomUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'dashboard.change_room'
    template_name = "tabs/room/room_update.html"
    model = Room
    form_class = RoomForm
    success_url	= '/dashboard/room/list/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
        

class RoomDeleteAPIView(DestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
        
    
class RoomViewPage(UserAccessMixin, ListView):
    permission_required = 'dashboard.view_room'
    template_name = "tabs/room/room_list.html"
    serializer_class = RoomSerializer
    model = Room
    queryset = Room.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.filter(user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data



class SendSMSAPIView(APIView):
    def post(self, request):
        sms_to = request.POST.get('sms_to')
        sms_text = request.POST.get('sms_text')

        if not sms_to:
            return JsonResponse({"status": "ERROR", "msg": "Mobile Number is required."})

        if not sms_text:
            return JsonResponse({"status": "ERROR", "msg": "SMS Content is required."})

        unicode = 'false'
        message_type = 'text'
        sms_text = urllib.parse.quote(sms_text)
        url_sms = f"https://pgapi.vispl.in/fe/api/v1/send?username={settings.SMS_USERNAME}&password={settings.SMS_PASSWORD}&unicode={unicode}&from={settings.SMS_FROM}&to={sms_to}&dltPrincipalEntityId={settings.SMS_DLT_PRINCIPAL_ID}&dltContentId={settings.SMS_DLT_CONTENT_ID}&text={sms_text}"
        

        try:
            with urlopen(url_sms) as response:
                sms_return = json.loads(response.read())
                if sms_return['state'] == "SUBMIT_ACCEPTED":
                    return JsonResponse({"status": "SUCCESS", "msg": f"SMS has been sent successfully to {sms_to}.", "response": sms_return})
                else:
                    return JsonResponse({"status": "ERROR", "msg": "Failed to send SMS.", "response": sms_return})
        except Exception as e:
            return JsonResponse({"status": "ERROR", "msg": f"Failed to send SMS: {str(e)}"})


"""
Foods View
"""
class FoodPriceModelView(viewsets.ModelViewSet):
    authentication_classes = [] 
    permission_classes = []
    serializer_class = PriceSerializer
    
    def get_queryset(self):
        return Price.objects.all()
        
    
class FoodsItemCreateView(UserAccessMixin, CreateView):
    permission_required = 'stores.add_item'
    template_name = "tabs/foods/item/item_add.html"
    model = Item
    form_class = FoodsItemForm
    success_url	= '/dashboard/foods/items/'
    
    def get_form_kwargs(self):
        kwargs = super(FoodsItemCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

class FoodsItemUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'stores.change_item'
    template_name = "tabs/foods/item/item_update.html"
    model = Item
    form_class = FoodsItemForm
    success_url	= '/dashboard/foods/items/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs



class FoodsItemDeleteView(UserAccessMixin, DeleteView):
    permission_required = 'stores.delete_item'
    model = Item
    success_url = reverse_lazy('/dashboard/foods/items/')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'message': 'Object deleted successfully'})

    
    
class FoodsItemsViewPage(UserAccessMixin, ListView):
    permission_required = 'stores.view_item'
    template_name = "tabs/foods/item/items_list.html"
    serializer_class = FoodItemsSerializer
    model = Item
    queryset = Item.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.filter(user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data


class FoodsCategoryCreateView(UserAccessMixin, CreateView):
    permission_required = 'stores.add_category'
    template_name = "tabs/foods/category/category_add.html"
    model = Category
    form_class = FoodsCategoryForm
    success_url	= '/dashboard/foods/categories/'



class FoodsCategoryUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'stores.change_category'
    template_name = "tabs/foods/category/category_update.html"
    model = Category
    form_class = FoodsCategoryForm
    success_url	= '/dashboard/foods/categories/'
    

class FoodsCategoryDeleteView(UserAccessMixin, DeleteView):
    permission_required = 'stores.delete_category'
    model = Category
    success_url = reverse_lazy('/dashboard/foods/categories/')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'message': 'Object deleted successfully'})

    

class FoodsCategoriesViewPage(UserAccessMixin, ListView):
    permission_required = 'stores.view_category'
    template_name = "tabs/foods/category/categories_list.html"
    serializer_class = FoodCategoriesSerializer
    model = Category
    queryset = Category.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.filter(user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data
    


"""
  #Sub Categories View
"""
class SubcategoryView(View):
    def get(self, request):
        category_id = request.GET.get('category_id')
        subcategories = SubCategory.objects.filter(category__id=category_id)

        subcategory_options = ''
        for subcategory in subcategories:
            subcategory_options += f'<option value="{subcategory.id}">{subcategory.name}</option>'

        return JsonResponse(subcategory_options, safe=False)
    
    
    
class FoodsSubCategoriesViewPage(UserAccessMixin, ListView):
    permission_required = 'stores.view_subcategory'
    template_name = "tabs/foods/sub_category/sub_categories_list.html"
    serializer_class = FoodSubCategoriesSerializer
    model = SubCategory
    queryset = SubCategory.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.filter(category__user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data


class FoodsSubCategoryCreateView(UserAccessMixin, CreateView):
    permission_required = 'stores.add_subcategory'
    template_name = "tabs/foods/sub_category/sub_category_add.html"
    model = SubCategory
    form_class = SubCategoryForm
    success_url	= '/dashboard/foods/categories/sub-categories/'
    
    def get_form_kwargs(self):
        kwargs = super(FoodsSubCategoryCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

class FoodsSubCategoryUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'stores.change_subcategory'
    template_name = "tabs/foods/sub_category/sub_category_update.html"
    model = SubCategory
    form_class = SubCategoryForm
    success_url	= '/dashboard/foods/categories/sub-categories/'
    
    def get_form_kwargs(self):
        kwargs = super(FoodsSubCategoryUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

class FoodsSubCategoryDeleteView(UserAccessMixin, DeleteView):
    permission_required = 'stores.delete_subcategory'
    model = SubCategory
    success_url = reverse_lazy('/dashboard/foods/categories/sub-categories/')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'message': 'Object deleted successfully'})
    


class FoodsOrdersViewPage(UserAccessMixin, ListView):
    permission_required = 'stores.view_order'
    template_name = "tabs/foods/order/order_list.html"
    serializer_class = FoodOrdersSerializer
    model = Order
    queryset = Order.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            get_rooms = Room.objects.filter(user=self.request.user)
            object_list = self.model.objects.filter(room__in=get_rooms)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data


class OrderExportPageView(UserAccessMixin, APIView):
    permission_required = 'stores.view_order'
    serializer_class = FoodOrdersSerializer

    # queryset = Admission.objects.all()
    # paginate_by = 10

    def post(self, request, pk):
        try:
            query = Order.objects.get(id=pk)
            data = FoodOrdersSerializer(query);
            return Response(data=data.data)
        except Order.DoesNotExist:
            return Response(data={"error": "Invalid Format of data"}, status=status.HTTP_400_BAD_REQUEST)
        
    

"""
Service page
"""
class ServiceViewPage(UserAccessMixin, ListView):
    permission_required = 'stores.view_item'
    template_name = "tabs/services/services_list.html"
    serializer_class = ServiceSerializer
    model = Service
    queryset = Service.objects.all()

    def get_queryset(self):
        object_list = self.model.objects.filter(user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data


class ServiceCreateView(UserAccessMixin, CreateView):
    permission_required = 'dashboard.add_service'
    template_name = "tabs/services/add_service.html"
    model = Service
    form_class = ServiceForm
    success_url	= '/dashboard/services/'


class ServiceUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'dashboard.change_service'
    template_name = "tabs/services/update_service.html"
    model = Service
    form_class = ServiceForm
    success_url	= '/dashboard/services/'
    

class ServiceDeleteAPIView(UserAccessMixin, DestroyAPIView):
    permission_required = 'dashboard.delete_service'
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class ServiceOrdersViewPage(UserAccessMixin, ListView):
    permission_required = 'stores.change_serviceorder'
    template_name = "tabs/services/order/order_list.html"
    serializer_class = ServiceOrdersSerializer
    model = ServiceOrder
    queryset = ServiceOrder.objects.all()

    def get_queryset(self):
        get_rooms = Room.objects.filter(user=self.request.user)
        object_list = self.model.objects.filter(room__in=get_rooms)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data


"""
Complaints View
"""
class ComplaintsViewPage(UserAccessMixin, ListView):
    permission_required = 'dashboard.view_complain'
    template_name = "tabs/complain/complain_list.html"
    serializer_class = ComplainSerializer
    model = Complain
    queryset = Complain.objects.all()

    def get_queryset(self):
        object_list = self.model.objects.filter(room__user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data
    

class ComplaintsUpdateAPIView(UserAccessMixin, UpdateAPIView):
    permission_required = 'dashboard.change_complain'
    queryset = Complain.objects.all()
    serializer_class = UpdateComplainSerializer

        

class ComplaintsDeleteAPIView(UserAccessMixin, DestroyAPIView):
    permission_required = 'dashboard.delete_complain'
    queryset = Complain.objects.all()
    serializer_class = ComplainSerializer
    


class ComplainTypesViewPage(UserAccessMixin, ListView):
    permission_required = 'dashboard.view_complaintype'
    template_name = "tabs/complain/complain_type_list.html"
    serializer_class = ComplainTypeSerializer
    model = ComplainType
    queryset = ComplainType.objects.all()

    def get_queryset(self):
        object_list = self.model.objects.filter(user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data



class ComplainTypeCreateView(UserAccessMixin, CreateView):
    permission_required = 'dashboard.add_complaintype'
    template_name = "tabs/complain/complain_type_add.html"
    model = ComplainType
    form_class = ComplainTypeForm
    success_url	= '/dashboard/complaints/types/'
    

class ComplainTypeUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'dashboard.change_complaintype'
    template_name = "tabs/complain/complain_type_update.html"
    model = ComplainType
    form_class = ComplainTypeForm
    success_url	= '/dashboard/complaints/types/'
    

class ComplainTypeDeleteAPIView(UserAccessMixin, DestroyAPIView):
    permission_required = 'dashboard.delete_complaintype'
    queryset = ComplainType.objects.all()
    serializer_class = ComplainTypeSerializer
    

"""
Dialer View
"""
class DialerCreateView(UserAccessMixin, CreateView):
    permission_required = 'dashboard.add_dialer'
    template_name = "tabs/dialer/dialer_add.html"
    model = Dialer
    form_class = DialerForm
    success_url	= '/dashboard/dialer/'
    
    def get_form_kwargs(self):
        kwargs = super(DialerCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    
class DialerViewPage(UserAccessMixin, ListView):
    permission_required = 'dashboard.view_dialer'
    template_name = "tabs/dialer/dialer_list.html"
    serializer_class = DialerSerializer
    model = Dialer
    queryset = Dialer.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.filter(extension__user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data



class DialerUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'dashboard.change_dialer'
    template_name = "tabs/dialer/dialer_update.html"
    model = Dialer
    form_class = DialerForm
    success_url	= '/dashboard/dialer/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    

class DialerDeleteAPIView(UserAccessMixin, DestroyAPIView):
    permission_required = 'dashboard.delete_dialer'
    queryset = Dialer.objects.all()
    serializer_class = DialerSerializer
    

        

"""
Exceptions
"""
class ExtensionCreateView(UserAccessMixin, CreateView):
    permission_required = 'dashboard.add_extension'
    template_name = "tabs/extension/extension_add.html"
    model = Extension
    form_class = ExtensionForm
    success_url	= '/dashboard/extension/'
    
    def get_form_kwargs(self):
        kwargs = super(ExtensionCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    
class ExtensionViewPage(UserAccessMixin, ListView):
    permission_required = 'dashboard.view_extension'
    template_name = "tabs/extension/extension_list.html"
    serializer_class = ExtensionSerializer
    model = Extension
    queryset = Extension.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.filter(user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data
    

class ExtensionUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'dashboard.change_extension'
    template_name = "tabs/extension/extension_update.html"
    model = Extension
    form_class = ExtensionForm
    success_url	= '/dashboard/extension/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs



class ExtensionDeleteAPIView(UserAccessMixin, DestroyAPIView):
    permission_required = 'dashboard.delete_extension'
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer
     
    

"""
Configuration View
"""

class PbxCreateView(UserAccessMixin, CreateView):
    permission_required = 'dashboard.add_pbx'
    template_name = "tabs/configuration/pbx_servers/pbx_server_add.html"
    model = Pbx
    form_class = PbxForm
    success_url	= '/dashboard/configuration/pbx/'
    
    
    
class PbxViewPage(UserAccessMixin, ListView):
    permission_required = 'dashboard.view_pbx'
    template_name = "tabs/configuration/pbx_servers/pbx_servers_list.html"
    serializer_class = PbxSerializer
    model = Pbx
    queryset = Pbx.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.filter(user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data



class PbxUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'dashboard.change_pbx'
    template_name = "tabs/configuration/pbx_servers/pbx_server_update.html"
    model = Pbx
    form_class = PbxForm
    success_url	= '/dashboard/configuration/pbx/'
    

class PbxDeleteView(UserAccessMixin, DeleteView):
    permission_required = 'dashboard.delete_pbx'
    model = Pbx
    success_url = reverse_lazy('/dashboard/configuration/pbx/')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'message': 'Object deleted successfully'})


    


class JanusCreateView(UserAccessMixin, CreateView):
    permission_required = 'dashboard.add_janus'
    template_name = "tabs/configuration/janus_gateways/janus_gateways_add.html"
    model = Janus
    form_class = JanusForm
    success_url	= '/dashboard/configuration/janus/'
        


class JanusViewPage(UserAccessMixin, ListView):
    permission_required = 'dashboard.view_janus'
    template_name = "tabs/configuration/janus_gateways/janus_gateways_list.html"
    serializer_class = JanusSerializer
    model = Janus
    queryset = Janus.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.filter(user=self.request.user)
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data
    
    
class JanusUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'dashboard.change_janus'
    template_name = "tabs/configuration/janus_gateways/janus_gateways_update.html"
    model = Janus
    form_class = JanusForm
    success_url	= '/dashboard/configuration/janus/'
    

class JanusDeleteView(UserAccessMixin, DeleteView):
    permission_required = 'dashboard.delete_janus'
    model = Janus
    success_url = reverse_lazy('/dashboard/configuration/janus/')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'message': 'Object deleted successfully'})
    
    
    
class GlobalUpdateAPIView(UserAccessMixin, UpdateAPIView):
    queryset = Global.objects.all()
    # serializer_class = GlobalUpdateSerializer
    def update(self, request,  *args, **kwargs):
        instance  = self.get_object()
        instance.config_value = request.data.get('config_value', json.loads(request.body).get('config_value'))
        if instance.config_value == 'Y':
            Room.objects.filter(user=self.request.user).update(status=True)
        else:
            Room.objects.filter(user=self.request.user).update(status=False)
        instance.save()
        return Response("Configuration Saved")
    

class GlobalViewPage(UserAccessMixin, ListView):
    permission_required = 'dashboard.view_global'
    template_name = "tabs/configuration/global_configuration/global_list.html"
    serializer_class = GlobalSerializer
    model = Global
    queryset = Global.objects.all()

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            object_list = self.model.objects.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(user_type__icontains=q) | Q(user_id__icontains=q)
            )
        else:
            object_list = self.model.objects.filter(user=self.request.user)
            
        return self.serializer_class(object_list, context={'request': self.request}, many=True).data
    
    

"""
Report Order View
"""
class OrderReportView(UserAccessMixin, FilterView):
    permission_required = 'stores.view_order'
    model = Order
    template_name = 'tabs/reports/order_report.html'
    filterset_class = OrderFilter
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = self.get_queryset()
        # context['orders_placed'] = orders.count()
        # context['orders_delivered'] = orders.filter(status='delivered').count()
        # context['orders_canceled'] = orders.filter(status='canceled').count()
        return context
    
    def post(self, request, *args, **kwargs):
        # Get the date range from the URL parameters
        get_model = request.POST.get('model')
        print(get_model)
        get_start_date = request.POST.get('start_date')
        get_end_date = request.POST.get('end_date')
        
        start_date = datetime.strptime(get_start_date, '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(get_end_date, '%Y-%m-%dT%H:%M')
        
        
        # Generate the file name based on the date range
        file_name = f'order_report_{start_date.date()}_to_{end_date.date()}.xlsx'
        if get_model == "food_orders":
           orders = self.get_queryset().filter(created_at__range=[start_date, end_date])
           
           
           # Create a dictionary to store order data grouped by date
           status = ["Ordered", "Processing", "Completed", "Canceled"]
           data = []
           for order in orders:
               create_at = order.created_at.strftime('%Y-%m-%dT%H:%M')
               updated_at = order.updated_at.strftime('%Y-%m-%dT%H:%M')
               order_quantity_and_title = []
               time_taken =  order.updated_at - order.created_at
               hours = time_taken.days * 24 + time_taken.seconds // 3600
               minutes = (time_taken.seconds % 3600) // 60
               
               for item in order.items.all():
                   item_title = f"{item.quantity} {item.item.title}"
                   order_quantity_and_title.append(item_title)
               
                   
               new_data = {'order_date_time': create_at, 'status': status[order.status], 'delivery_date_time': updated_at, 
                           'from_room_number': order.room.room_number, "order_description": f"Room  {order.room.room_number} orders {','.join(order_quantity_and_title)}", 
                           "comment_by_staff": order.note, "total_time_taken": f"{hours}:{minutes}"}
               data.append(new_data)
               
           header = ['Order DateTime', 'Status', 'Delivery DateTime', 'From RoomNumber', 'Order Description', 'Comment ByStaff', 'Total TimeTaken']
        elif get_model == "service_orders":
            orders = ServiceOrder.objects.filter(created_at__range=[start_date, end_date])
            
            status = ["Ordered", "Processing", "Completed", "Canceled"]
            data = []
            for order in orders:
                create_at = order.created_at.strftime('%Y-%m-%dT%H:%M')
                updated_at = order.updated_at.strftime('%Y-%m-%dT%H:%M')
                order_quantity_and_title = []
                time_taken =  order.updated_at - order.created_at
                hours = time_taken.days * 24 + time_taken.seconds // 3600
                minutes = (time_taken.seconds % 3600) // 60
                
                for service in order.services.all():
                    service_title = f"{service.quantity} {service.service.name}"
                    order_quantity_and_title.append(service_title)
                
                    
                new_data = {'order_date_time': create_at, 'status': status[order.status], 'delivery_date_time': updated_at, 
                            'from_room_number': order.room.room_number, "order_description": f"Room  {order.room.room_number} orders {','.join(order_quantity_and_title)}", 
                            "comment_by_staff": order.note, "total_time_taken": f"{hours}:{minutes}"}
                data.append(new_data)
                
            header = ['Service Request DateTime', 'Status', 'Delivery DateTime', 'From RoomNumber', 'Order Description', 'Comment ByStaff', 'Total TimeTaken']
        
        elif get_model == "complaints":
            orders = Complain.objects.filter(created_at__range=[start_date, end_date])
            
            status = ["Complained", "Processing", "Completed", "Canceled"]
            data = []
            for order in orders:
                create_at = order.created_at.strftime('%Y-%m-%dT%H:%M')
                updated_at = order.updated_at.strftime('%Y-%m-%dT%H:%M')
                complain = order.complain.title
                time_taken =  order.updated_at - order.created_at
                hours = time_taken.days * 24 + time_taken.seconds // 3600
                minutes = (time_taken.seconds % 3600) // 60
                
                
                    
                new_data = {'order_date_time': create_at, 'status': status[order.status], 'delivery_date_time': updated_at, 
                            'from_room_number': order.room.room_number, "order_description": f"Room  {order.room.room_number} complain {complain}", 
                            "comment_by_staff": order.note, "total_time_taken": f"{hours}:{minutes}"}
                data.append(new_data)
                
            header = ['Complaint DateTime', 'Status', 'Complaint Resolves DateTime', 'From RoomNumber', 'Complaint Description', 'Comment ByStaff', 'Total TimeTaken']
            
            
        return JsonResponse(data={"data": data, "header": header, "filename": file_name})