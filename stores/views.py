import json
import os
import string
import random
import traceback
from urllib import response
from dashboard.models import *
import uuid
from django.http import HttpResponseBadRequest
import base64
from hashlib import sha256
import requests

from django.core.mail import send_mail

from accounts.models import User
from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView,
    DetailView,
    TemplateView,
)
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core import settings
from dashboard.forms import ComplainForm
from dashboard.models import Complain, Dialer, Room, Service
from dashboard.serializers import (
    ComplainSerializer,
    ExtensionSerializer,
    FoodCategoriesSerializer,
    FoodItemsSerializer,
    FoodOutdoorOrdersSerializer,
    FoodOrdersSerializer,
    FoodSubCategoriesSerializer,
    PhoneDialerSerializer,
    ServiceSerializer,
)
from stores.models import (
    Cart,
    Temporary_Users,
    OutdoorCart,
    Category,
    Item,
    Order,
    OutdoorOrder,
    OrderItem,
    OutdoorOrderItem,
    Price,
    ServiceCart,
    ServiceOrder,
    ServiceOrderItem,
    SubCategory,
)
from stores.serializers import (
    CartItemSerializer,
    OutdoorCartItemSerializer,
    CartSerializer,
    OutdoorCartSerializer,
    CustomOrderSerializer,
    CustomOutdoorOrderSerializer,
    GetServiceCartSerializer,
    ItemSerializer,
    OrderSerializer,
    OutdoorOrderSerializer,
    ServiceCartSerializer,
    ServiceOrderSerializer,
    ServiceOrdersSerializer,
    ServiceUpdateOrderSerializer,
    UpdateOrderSerializer,
    UpdateOutdoorOrderSerializer
)


# import sys
# if sys.platform == 'linux':
#     import telegram
#     from telegram import ParseMode

from notification.helpers import push_notification, telegram_notification



from firebase_admin import credentials, messaging
import firebase_admin

credentials_path = os.path.join(settings.BASE_DIR, "stores", "credentials.json")
# Initialize Firebase Admin SDK
cred = credentials.Certificate(credentials_path)
firebase_admin.initialize_app(cred)


# Create your views here.
# def showFirebaseJS(request):
#     file_path = os.path.join(
#         settings.BASE_DIR, "static", "js", "firebase-messaging-sw.js"
#     )
#     with open(file_path, "r") as file:
#         js_content = file.read()

#     return HttpResponse(js_content, content_type="application/javascript")


class NotFoundPageView(TemplateView):
    template_name = "pages/page-404.html"


class ModulesViewPage(TemplateView):
    template_name = "modules/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def filterItemByCategories(user, categories=None, sub_category=None, item_type=None, search=None):
    items = []
    if sub_category:
        new_item = {}
        base_query = Q(user=user, sub_category=sub_category)
        if item_type:
            if item_type == "Day Deal":
                base_query &= Q(prices__sell_price__isnull=False)
            else:
                base_query &= Q(item_type=item_type)

        filtered_items = Item.objects.filter(base_query).distinct()

        if filtered_items.exists():
            new_item["items"] = FoodItemsSerializer(filtered_items, many=True).data
            items.append(new_item)
    else:
        for item_category in categories:
            new_item = {"category": item_category.name}

            base_query = Q(user=user, category=item_category)

            if search:
                base_query &= Q(title__icontains=search)
            elif item_type:
                if item_type == "Day Deal":
                    base_query &= Q(prices__sell_price__isnull=False)
                else:
                    base_query &= Q(item_type=item_type)

            filtered_items = Item.objects.filter(base_query).distinct()

            if filtered_items.exists():
                new_item["items"] = FoodItemsSerializer(filtered_items, many=True).data
                items.append(new_item)

    return items


class FoodsPageView(TemplateView):
    template_name = "modules/foods_menu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("room_token")
        flag = False
        if pk:
            try:
                room = Room.objects.get(room_token=pk)
            except Room.DoesNotExist:
                try:
                    room = User.objects.get(outdoor_token=pk)
                    flag = True
                except User.DoesNotExist:
                    raise Http404("Store does not exist.")
        else:
            raise Http404("Store does not exist.")

        if room and flag is False:
            try:
                bar_enabled = Category.objects.filter(user=room.user, name="Bar").exists()
            except Category.DoesNotExist:
                bar_enabled = False
        else:
            try:
                bar_enabled = Category.objects.filter(user=room, name="Bar").exists()
            except Category.DoesNotExist:
                bar_enabled = False

        if flag is True:
            context['outdoor_token'] = True
        context["bar_enabled"] = bar_enabled
        return context


class HomeViewPage(TemplateView):
    # model = Category
    template_name = "navs/home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_filter = self.request.GET.get("category")
        sub_category_filter = self.request.GET.get("sub_category")
        item_type = self.request.GET.get("item_type")
        get_sub_category = None
        search = self.request.GET.get("q")
        pk = self.kwargs.get("room_token")
        if pk:
            try:
                room = Room.objects.get(room_token=pk)
            except Room.DoesNotExist:
                raise Http404("Store does not exist.")
        else:
            raise Http404("Store does not exist.")

        get_categories = Category.objects.filter(user=room.user).exclude(
            name__in=["Bar"]
        )
        # Filter Item by Sub Category
        if sub_category_filter:
            try:
                get_sub_category = SubCategory.objects.filter(name=sub_category_filter)
                if item_type:
                    items = filterItemByCategories(
                        room.user, sub_category=get_sub_category[0], item_type=item_type
                    )
                else:
                    items = filterItemByCategories(
                        room.user, sub_category=get_sub_category[0]
                    )
            except SubCategory.DoesNotExist:
                items = filterItemByCategories(room.user, get_categories)
        # Filter Item by Category
        elif category_filter:
            try:
                category = Category.objects.filter(
                    user=room.user, name=category_filter
                ).exclude(name__in=["Bar"])
                get_sub_category = SubCategory.objects.filter(category=category[0])

                if item_type:
                    items = filterItemByCategories(
                        room.user, category, item_type=item_type
                    )
                else:
                    items = filterItemByCategories(room.user, category)
            except Category.DoesNotExist:
                items = filterItemByCategories(room.user, get_categories)
        # Filter by Item Type
        elif item_type:
            items = filterItemByCategories(
                room.user, categories=get_categories, item_type=item_type
            )
        # Filter Item By Search
        elif search:
            items = filterItemByCategories(room.user, get_categories, search=search)
        else:
            items = filterItemByCategories(room.user, get_categories)

        get_cart_items = Cart.objects.filter(room=room)

        # calculating amount before tax
        amount = sum(item.price * item.quantity for item in get_cart_items)
        # calculating tax on each item
        total_tax = round(sum((item.item.tax_rate / 100) * (item.price * item.quantity) for item in get_cart_items), 2)
        # calculating amount after tax
        total_price_including_tax = amount + total_tax

        # amounts = sum(item.price * item.quantity for item in get_cart_items)
        context["categories"] = FoodCategoriesSerializer(
            get_categories.exclude(name__in=["Bar", "Veg", "Non Veg"]), many=True
        ).data
        context["sub_categories"] = FoodSubCategoriesSerializer(
            get_sub_category, many=True
        ).data
        context["items"] = items
        context["room_id"] = room.id
        context["cart_items"] = CartItemSerializer(get_cart_items, many=True).data
        # total item amount
        context["items_amount"] = amount
        # overall gst charged 
        context["total_tax"] = total_tax
        # checkout amount
        context["total_price"] = total_price_including_tax
        context["logo"] = room.user.picture.url
        context["hotel_name"] = room.user.username

        return context


class OutdoorHomeViewPage(TemplateView):
    template_name = "navs/home/outdoor_index.html"

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            category_filter = self.request.GET.get("category")
            sub_category_filter = self.request.GET.get("sub_category")
            item_type = self.request.GET.get("item_type")
            search = self.request.GET.get("q")
            get_sub_category = None
            pk = self.kwargs.get("room_token")
            if pk:
                try:
                    room = User.objects.get(outdoor_token=pk)
                    # check if anonymous id already exist
                    if 'anonymous_user_id' not in self.request.session:
                        self.request.session['anonymous_user_id'] = ''.join(random.choices(string.ascii_uppercase+string.digits, k=12))
                        temp_user_id = Temporary_Users.objects.create(
                            anonymous_user_id=self.request.session['anonymous_user_id']
                        )
                    else:
                        temp_user_id = Temporary_Users.objects.get(
                            anonymous_user_id=self.request.session['anonymous_user_id']
                        )
                except User.DoesNotExist:
                    raise Http404("Store does not exist.")
            else:
                raise Http404("Store does not exist.")

            get_categories = Category.objects.filter(user=room).exclude(
                name__in=["Bar"]
            )
            # Filter Item by Sub Category
            if sub_category_filter:
                try:
                    get_sub_category = SubCategory.objects.filter(name=sub_category_filter)
                    if item_type:
                        items = filterItemByCategories(
                            room, sub_category=get_sub_category[0], item_type=item_type
                        )
                    else:
                        items = filterItemByCategories(
                            room, sub_category=get_sub_category[0]
                        )
                except SubCategory.DoesNotExist:
                    items = filterItemByCategories(room, get_categories)

            # Filter Item by Category
            elif category_filter:
                try:
                    category = Category.objects.filter(
                        user=room, name=category_filter
                    ).exclude(name__in=["Bar"])
                    get_sub_category = SubCategory.objects.filter(category=category[0])

                    if item_type:
                        items = filterItemByCategories(
                            room, category, item_type=item_type
                        )
                    else:
                        items = filterItemByCategories(room, category)
                except Category.DoesNotExist:
                    items = filterItemByCategories(room, get_categories)

            # Filter by Item Type
            elif item_type:
                items = filterItemByCategories(
                    room, categories=get_categories, item_type=item_type
                )
            # Filter Item By Search
            elif search:
                items = filterItemByCategories(room, get_categories, search=search)
            else:
                items = filterItemByCategories(room, get_categories)

            
            get_cart_items = OutdoorCart.objects.filter(user=room, anonymous_user_id=temp_user_id.anonymous_user_id)
            # calculating amount for price basis on their qty
            amount = sum(item.price * item.quantity for item in get_cart_items)
            total_tax = round(sum((item.item.tax_rate / 100) * (item.price * item.quantity) for item in get_cart_items), 2)

            
            total_price_including_tax = amount + total_tax

            # calculating tax basis on tax_rate for each item
            # total_tax = 0
            # for item in get_cart_items:
            #     item_tax_rate = item.item.tax_rate
            #     # print("item_tax_rate", item_tax_rate)
            #     item_total_price = item.price * item.quantity
            #     item_tax = (item_tax_rate / 100) * item_total_price
            #     # print("item_tax", item_tax)
            #     total_tax += item_tax

            # print("total_tax", total_tax)

            # Total price including tax
            # total_price_including_tax = amounts + total_tax
            # print("total_price_including_tax", total_price_including_tax)s


            context["categories"] = FoodCategoriesSerializer(
                get_categories.exclude(name__in=["Bar", "Veg", "Non Veg"]), many=True
            ).data
            context["sub_categories"] = FoodSubCategoriesSerializer(
                get_sub_category, many=True
            ).data
            outdoor_token = User.objects.get(outdoor_token=pk)
            context['user'] = room
            context['phone'] = outdoor_token.phone
            context["items"] = items
            context["room_id"] = pk
            context["cart_items"] = OutdoorCartItemSerializer(get_cart_items, many=True).data
            # total item amount
            context["items_amount"] = amount
            # overall gst charged 
            context["total_tax"] = total_tax
            # checkout amount
            context["total_price"] = total_price_including_tax
            if room.picture is not None:
                context['picture'] = room.picture.url
            else:
                context['picture'] = None
            context['hotel_name'] = room.username
            context["anonymous_user_id"] = temp_user_id.anonymous_user_id
            context["razorpay_clientid"] = room.razorpay_clientid
            context["razorpay_clientsecret"] = room.razorpay_clientsecret
            # print("context", context)
            return context
        except:
            import traceback
            telegram_notification("iberry2023", traceback.format_exc())
            traceback.print_exc()



# phonepe payment gateway integration 
import uuid  
from hashlib import sha256
import base64



def CreatePaymentOrder(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            merchantTransactionId = ''.join(random.choices(string.ascii_letters+string.digits, k=16))
            merchantUserId = ''.join(random.choices(string.ascii_letters+string.digits, k=16))
            user = User.objects.get(outdoor_token=body['user'])

            cart_items = OutdoorCart.objects.filter(anonymous_user_id=body['anonymous_user_id'])
            cart_total = sum([item.quantity * item.price for item in cart_items])
            total_tax = round(sum((item.item.tax_rate / 100) * (item.price * item.quantity) for item in cart_items), 2)
            receipt = ''.join(random.choices(string.ascii_letters+string.digits, k=16))
            amount = cart_total + total_tax
            amount = int(amount * 100)

            # "callbackUrl": f"{request.scheme}://{request.get_host()}/payment/checkout?token={body['user']}&user_id={body['anonymous_user_id']}",
            payload = {
                "merchantId":  user.razorpay_clientid,
                "merchantTransactionId": merchantTransactionId,
                "merchantUserId": merchantUserId,
                "amount": amount,
                "redirectUrl": f"{request.scheme}://{request.get_host()}/payment/checkout?token={body['user']}&user_id={body['anonymous_user_id']}",
                "redirectMode": "POST",
                "callbackUrl": f"{request.scheme}://{request.get_host()}/payment/checkout/success",
                "paymentInstrument": {
                    "type": "PAY_PAGE"
                }
            }
            json_str = json.dumps(payload)
            # Encode the string as bytes
            json_bytes = json_str.encode('utf-8')
            # Encode the bytes using base64
            base64_encoded = base64.b64encode(json_bytes)
            # Convert bytes to string (if needed)
            base64_encoded_str = base64_encoded.decode('utf-8') + "/pg/v1/pay" + user.razorpay_clientsecret
            verify_header = sha256(base64_encoded_str.encode()).hexdigest() + '###' + '1'
            headers = {
                'Content-Type': 'application/json',
                'X-VERIFY': verify_header
            }
            # url = "https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay"
            url = "https://api.phonepe.com/apis/hermes/pg/v1/pay"

            # if os.environ.get('ENV') == 'dev':
            #     # phonpe test api
            #     url = "https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay"
            # else:
            #     # phonepe prod api
            #     url = "https://api.phonepe.com/apis/hermes/pg/v1/pay"

            data = {
                'request': base64_encoded.decode('utf-8')
            }
            
            result = requests.post(url, json=data, headers=headers)

            if result.status_code == 200:
                response_data = result.json()  # Extracting JSON data from the response
                result_url = response_data.get('data', {}).get('instrumentResponse', {}).get('redirectInfo', {}).get('url')
                if result_url:
                    temp_user = Temporary_Users.objects.get(anonymous_user_id=body['anonymous_user_id'])
                    temp_user.receipt = receipt
                    temp_user.order_total = str(cart_total * 100)
                    temp_user.customer_name = body['username']
                    temp_user.customer_email = body['email']
                    temp_user.customer_phone = body['phone']
                    temp_user.customer_address = body['address']
                    temp_user.save()
                    return JsonResponse({
                            'status': True,
                            'uri': result_url
                        })

        except:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'status': False,
                'traceback': json.dumps(traceback.format_exc())
            })



@csrf_exempt
def paymentCheckout(request):
    try:
        if request.method == 'POST':
            payload = request.POST
            if payload['code'] == 'PAYMENT_SUCCESS':
                get_room = User.objects.get(outdoor_token=request.GET.get('token'))
                cart_items = OutdoorCart.objects.filter(user=get_room, anonymous_user_id=request.GET.get('user_id'))
                if cart_items:
                    order_id = str(uuid.uuid4().int & (10**8 - 1))
                    order = OutdoorOrder.objects.create(order_id=order_id, user=get_room)
                    total_amount = 0
                    overall_tax = 0
                    for cart in cart_items:
                        item = cart.item
                        quantity = cart.quantity
                        total_amount += cart.price * quantity
                        overall_tax += (item.tax_rate / 100) * (cart.price * quantity)
                        order_item = OutdoorOrderItem.objects.create(
                            order=order, item=item, quantity=quantity, price=cart.price
                        )
                        order.items.add(order_item)

                    order.total_price = total_amount
                    order.overall_tax = overall_tax
                    order.save()
                    cart_items.delete()
                    # here i can associate the order_id in temp_users
                    temp_user = Temporary_Users.objects.get(anonymous_user_id=request.GET.get('user_id'))
                    temp_user.custom_order_id = order_id
                    temp_user.save()

                    # Send push notification
                    # message = f'A new order received'
                    # notification = messaging.Notification(
                    #     title=f'A new order received',
                    #     body=message,
                    # )
                    # message = messaging.Message(
                    #     notification=notification,
                    #     token=get_room.firebase_token
                    # )
                    # messaging.send(message)

                    # telegram notification for order received
                    order_list_url = f'{request.scheme}://{request.get_host()}/dashboard/foods/outdoor-orders/'
                    message = f'You have received an order. View the order list here: \n<a href="{order_list_url}">Click here</a>'
                    # channel_name = 'Iberry2023'
                    # telegram_notification(get_room.channel_name, message)             
                    telegram_notification(get_room.channel_name, get_room.bot_token, message)       

                    return redirect(reverse('stores:outdoor_order_status', kwargs={
                        'room_token': request.GET.get('token'),
                        'order_id': order_id
                    }))
            else:
                get_room = User.objects.get(outdoor_token=request.GET.get('token'))
                cart_items = OutdoorCart.objects.filter(user=get_room, anonymous_user_id=request.GET.get('user_id'))
                cart_items.delete()
                return redirect(reverse('stores:foods-outdoor-items', kwargs={
                    'room_token': request.GET.get('token')
                }))
    except:
        traceback.print_exc()




@csrf_exempt
def paymentCheckoutSuccess(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if code == 'PAYMENT_SUCCESS':
            return HttpResponse("Success")
        else:
            return HttpResponse("Failed, Try Again!")





class BarPageView(TemplateView):
    # model = Category
    template_name = "navs/home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_filter = self.request.GET.get("category")
        sub_category_filter = self.request.GET.get("sub_category")
        get_sub_categories = None
        search = self.request.GET.get("q")
        pk = self.kwargs.get("room_token")
        if pk:
            try:
                room = Room.objects.get(room_token=pk)
            except Room.DoesNotExist:
                raise Http404("Store does not exist.")
            # context['total_users'] = User.objects.all().count()
        else:
            raise Http404("Store does not exist.")

        get_category = Category.objects.filter(user=room.user, name="Bar")
        # Filter Item by Category
        if sub_category_filter:
            try:
                get_sub_categories = SubCategory.objects.filter(
                    category=get_category[0], name=sub_category_filter
                )
                items = filterItemByCategories(
                    room.user, sub_category=get_sub_categories[0]
                )
            except SubCategory.DoesNotExist:
                items = filterItemByCategories(room.user, categories=get_category)

        # Filter Item By Search
        elif search:
            items = filterItemByCategories(
                room.user, categories=get_category, search=search
            )

        else:
            get_sub_categories = SubCategory.objects.filter(category=get_category[0])
            items = filterItemByCategories(room.user, categories=get_category)

        get_cart_items = Cart.objects.filter(room=room)
        amounts = sum(item.price * item.quantity for item in get_cart_items)

        context["sub_categories"] = FoodSubCategoriesSerializer(
            get_sub_categories, many=True
        ).data
        context["items"] = items
        context["room_id"] = room.id
        context["cart_items"] = CartItemSerializer(get_cart_items, many=True).data
        context["total_price"] = amounts
        return context


class ProductDetailView(DetailView):
    model = Item
    template_name = "navs/home/item_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        pk = self.kwargs.get("room_token")
        if pk:
            try:
                room = Room.objects.get(room_token=pk)
            except Room.DoesNotExist:
                raise Http404("Store does not exist.")
        else:
            raise Http404("Store does not exist.")

        get_cart_items = Cart.objects.filter(room=room)
        amounts = sum(item.price * item.quantity for item in get_cart_items)

        # context['related_products'] = Item.objects.filter(category=product.category).exclude(product_id=product.product_id)[:6]
        context["item"] = ItemSerializer(
            product, context={"request": self.request}
        ).data
        context["room_id"] = room.id
        context["cart_items"] = CartItemSerializer(get_cart_items, many=True).data
        context["total_price"] = amounts
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(
            Item, id=self.kwargs["item_id"], created_at__lte=timezone.now()
        )


class CartModelView(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = CartSerializer

    def get_queryset(self):
        room_id = self.request.query_params.get("room_id")
        if room_id:
            return Cart.objects.filter(room=room_id)
        else:
            return Cart.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        object_id = instance.id
        return object_id

    def perform_update(self, serializer):
        # Custom logic to handle updates
        instance = serializer.save()
        return instance.id

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item_id = self.request.POST.get("item")
        price_id = self.request.POST.get("price")
        room_id = self.request.POST.get("room")

        item = Item.objects.get(id=item_id)
        price = 0
        if int(price_id) > 1:
            get_price = Price.objects.get(id=price_id)
            if get_price.sell_price:
                price = get_price.sell_price
            else:
                price = get_price.price
        else:
            get_price = item.prices.first()
            if get_price.sell_price:
                price = get_price.sell_price
            else:
                price = get_price.price

        additional_data = {
            "price": price,
        }
        for key, value in additional_data.items():
            serializer.validated_data[key] = value

        object_id = self.perform_create(serializer)
        room = Room.objects.get(id=room_id)
        get_cart_items = Cart.objects.filter(room=room)

        # Calculate total price and total items excluding tax(before checkout)
        amount = sum(item.price * item.quantity for item in get_cart_items)
        # calculate total no of items(quantity items)
        total_items = sum(item.quantity for item in get_cart_items)
        # calculate total gst tax for each item
        total_tax = round(sum((item.item.tax_rate / 100) * (item.price * item.quantity) for item in get_cart_items), 2)
        # calculate total amount including tax (checkout)
        total_price_including_tax = amount + total_tax
        
        # total_items = sum(item.quantity for item in cart_items)
        # amounts = sum(item.price * item.quantity for item in cart_items)
        extra_data = {
            "id": object_id,
            "items_amount": amount,
            "total_items": total_items,
            "total_tax": total_tax,
            "total_price": total_price_including_tax,
        }

        return Response(extra_data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        cart_id = self.kwargs["pk"]
        instance = self.get_object()
        cart = Cart.objects.get(id=cart_id)
        
        # Check if quantity is greater than 1
        if instance.quantity > 1:
            # Decrease quantity by 1
            instance.quantity -= 1
            instance.save()
        else:
            # Delete the cart item if quantity is 1
            self.perform_destroy(instance)
        # self.perform_destroy(instance)

        get_cart_items = Cart.objects.filter(room=cart.room)
        
        # Calculate total price and total items
        amount = sum(item.price * item.quantity for item in get_cart_items)
        # calculate total tax for each item
        total_tax = round(sum((item.item.tax_rate / 100) * (item.price * item.quantity) for item in get_cart_items),2)
        # calculate total amount including tax
        total_price_including_tax = amount + total_tax
        # calculate total no of items
        total_items = sum(item.quantity for item in get_cart_items)
        

        
        # amounts = sum(item.price * item.quantity for item in get_cart_items)
        # total_items = sum(item.quantity for item in get_cart_items)
        response_data = {
            "items_amount": amount,
            "total_items": total_items,
            "total_tax": total_tax,
            "total_price": total_price_including_tax,
        }
        return Response(response_data, status=status.HTTP_200_OK)

def OutdoorCartUserid(request):
    if request.method == 'POST':
        user_id =  ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
        return JsonResponse({
            'user_id': user_id
        })





class OutdoorCartModelView(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = OutdoorCartSerializer

    def get_queryset(self):
        room_id = self.request.query_params.get("room_id")
        user_id = self.request.query_params.get("user_id")
        if room_id and user_id:
            return OutdoorCart.objects.filter(user__outdoor_token=room_id, cart_user_id=user_id)
        else:
            return OutdoorCart.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        return instance.id

    def perform_update(self, serializer):
        # Custom logic to handle updates
        instance = serializer.save()
        return instance.id

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data={
                'user': User.objects.get(outdoor_token=request.data['user']).pk,
                'anonymous_user_id': request.data['anonymous_user_id'],
                'cart_user_id': request.data['cart_user_id'],
                'item': request.data['item'],
                'price': request.data['price'],
                'quantity': request.data['quantity'],
            })
            serializer.is_valid(raise_exception=True)
            item_id = self.request.POST.get("item")
            price_id = self.request.POST.get("price")
            room_id = self.request.POST.get("user")

            item = Item.objects.get(id=item_id)
            price = 0
            if int(price_id) > 1:
                get_price = Price.objects.get(id=price_id)
                if get_price.sell_price:
                    price = get_price.sell_price
                else:
                    price = get_price.price
            else:
                get_price = item.prices.first()
                if get_price.sell_price:
                    price = get_price.sell_price
                else:
                    price = get_price.price

            additional_data = {
                "price": price,
            }
            for key, value in additional_data.items():
                serializer.validated_data[key] = value

            object_id = self.perform_create(serializer)
            user = User.objects.get(outdoor_token=room_id)
            get_cart_items = OutdoorCart.objects.filter(user=user, cart_user_id=request.data.get('cart_user_id'))
            # total_items = sum(item.quantity for item in cart_items)
            # amounts = sum(item.price * item.quantity for item in cart_items)
            # Calculate total price and total items excluding tax(before checkout)
            amount = sum(item.price * item.quantity for item in get_cart_items)
            # calculate total gst tax for each item
            total_tax = round(sum((item.item.tax_rate / 100) * (item.price * item.quantity) for item in get_cart_items), 2)
            # calculate total amount including tax (checkout)
            total_price_including_tax = amount + total_tax
            # calculate total no of items(quantity items)
            total_items = sum(item.quantity for item in get_cart_items)

            extra_data = {
                "id": object_id,
                "total_items": total_items,
                "items_amount": amount,
                "total_tax": total_tax,
                "total_price": total_price_including_tax,
            }


            return Response(extra_data, status=status.HTTP_201_CREATED)
        except:
            import traceback
            traceback.print_exc()



    def destroy(self, request, *args, **kwargs):
        try:
            user_id = request.GET.get('user_id')
            cart_id = self.kwargs["pk"]
            instance = self.get_object()
            cart = OutdoorCart.objects.get(id=cart_id, cart_user_id=user_id)

            self.perform_destroy(instance)

            # Check if the cart is empty after deleting the item
            get_cart_items = OutdoorCart.objects.filter(user=cart.user, cart_user_id=user_id)
            if not get_cart_items.exists():
                cart.delete()

            # Calculate total price and total items
            amount = sum(item.price * item.quantity for item in get_cart_items)
            # calculate total tax for each item
            total_tax = round(sum((item.item.tax_rate / 100) * (item.price * item.quantity) for item in get_cart_items),2)
            # calculate total amount including tax
            total_price_including_tax = amount + total_tax
            # calculate total no of items
            total_items = sum(item.quantity for item in get_cart_items)

            response_data = {
                "total_items": total_items,
                "items_amount": amount,
                "total_tax": total_tax,
                "total_price": total_price_including_tax,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except OutdoorCart.DoesNotExist():
            traceback.print_exc()
            raise Http404("Cart not Found")
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    def decrement_quantity(self, request, *args, **kwargs):
        try:
            cart_id = kwargs['pk']
            instance = self.get_object()
            cart = OutdoorCart.objects.get(id=cart_id)

            if cart.quantity >= 1:
                cart.quantity -= 1
                cart.save()
            
             # Calculate total price and total items
            get_cart_items = OutdoorCart.objects.filter(user=cart.user)
            amount = sum(item.price * item.quantity for item in get_cart_items)
            total_items = sum(item.quantity for item in get_cart_items)
            total_tax = round(sum((item.item.tax_rate / 100) * (item.price * item.quantity) for item in get_cart_items), 2)
            total_price_including_tax = amount + total_tax


            response_data = {
                "total_items": total_items,
                "amount": amount,
                "total_tax": total_tax,
                "total_price": total_price_including_tax,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except:
            traceback.print_exc()
            return response({"error": "Cart is empty"}, status=status.HTTP_401_UNAUTHORIZED)



class OutdoorOrderView(viewsets.ModelViewSet):
    serializer_class = OutdoorOrderSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return UpdateOutdoorOrderSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        return OutdoorOrder.objects.all()

class OrderModelView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return UpdateOrderSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        return Order.objects.all()


class OutdoorOrderModelView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            get_room = User.objects.get(outdoor_token=data['user'])
            cart_items = OutdoorCart.objects.filter(user=get_room, anonymous_user_id=data['anonymous_user_id'])
            
            if cart_items:
                order_id = str(uuid.uuid4().int & (10**8 - 1))
                order = OutdoorOrder.objects.create(order_id=order_id, user=get_room)
                total_amount = 0
                overall_tax = 0
                for cart in cart_items:
                    item = cart.item
                    quantity = cart.quantity
                    total_amount += cart.price * quantity
                    overall_tax += (item.tax_rate / 100) * (cart.price * quantity)
                    order_item = OutdoorOrderItem.objects.create(
                        order=order, item=item, quantity=quantity, price=cart.price
                    )
                    order.items.add(order_item)

                order.total_price = total_amount
                order.overall_tax = round(overall_tax, 2)
                order.save()
                cart_items.delete()

                # here i can associate the order_id in temp_users
                temp_user = Temporary_Users.objects.get(anonymous_user_id=data['anonymous_user_id'])
                temp_user.custom_order_id = order_id
                temp_user.order_total = total_amount
                temp_user.customer_name = data['name']
                temp_user.customer_email = data['email']
                temp_user.customer_phone = data['phone']
                temp_user.customer_address = data['address']
                temp_user.save()


                # try:
                #     message = f'A new order received'
                #     notification = messaging.Notification(
                #         title=f'A new order received',
                #         body=message,
                #     )
                #     message = messaging.Message(
                #         notification=notification,
                #         token=get_room.firebase_token
                #     )
                #     messaging.send(message)
                #     message  =  'hi'
                #     telegram_notification(get_room.channel_name, get_room.bot_token, message)
                # except:
                #     telegram_notification(get_room.channel_name, get_room.bot_token, json.dumps(traceback.format_exc()))
                #     traceback.print_exc()
                
                try:
                    message = f'A new outdoor order received'
                    title = 'Outdoor Order received'
                    token = get_room.firebase_token
                    firebase_status = push_notification(message, title, token)
                except:
                    traceback.print_exc()
                
                
                # telegram notification
                order_list_url = f'{request.scheme}://{request.get_host()}/dashboard/foods/outdoor-orders/'
                message = f'You have received an outdoor order. View the order here:\n <a href="{order_list_url}">Click here</a>'
                # channel_name = 'Iberry2023'
                telegram_notification(get_room.channel_name, get_room.bot_token, message)

                return Response(
                    {
                        "success": "Order has been Placed.",
                        "room_id": request.data['user'],
                        "order_id": order_id,
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"error": "Cart is empty"}, status=status.HTTP_401_UNAUTHORIZED
                )
        except:
            traceback.print_exc()
            return Response({
                'success': "Order not being placed."
            })


@csrf_exempt
def PlaceOrderAPIView(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
            serializer = CustomOrderSerializer(data=data)
            if serializer.is_valid():
                get_room = Room.objects.get(id=serializer.data["room"])
                cart_items = Cart.objects.filter(room=get_room)
                if cart_items:
                    order_id = str(uuid.uuid4().int & (10**8 - 1))
                    order = Order.objects.create(order_id=order_id, room=get_room)
                    order.save()
                    total_amount = 0
                    overall_tax = 0
                    for cart in cart_items:
                        item = cart.item
                        quantity = cart.quantity
                        total_amount += cart.price * quantity
                        overall_tax += (item.tax_rate / 100) * (cart.price * quantity)
                        order_item = OrderItem.objects.create(
                            order=order, item=item, quantity=quantity, price=cart.price
                        )
                        order.items.add(order_item)

                    order.total_price = total_amount
                    order.overall_tax = round(overall_tax, 2)
                    order.save()
                    cart_items.delete()

                
                # here i can associate the order_id in temp_users
                # temp_user = Temporary_Users.objects.get(anonymous_user_id=data['anonymous_user_id'])
                # temp_user.custom_order_id = order_id
                # temp_user.order_total = total_amount
                # temp_user.customer_name = data['name']
                # temp_user.customer_email = data['email']
                # temp_user.customer_phone = data['phone']
                # temp_user.customer_address = data['address']
                # temp_user.save()
                
                # Send push notification
                try:
                    message = f'A new room order received'
                    title = 'Room Order received'
                    token = get_room.firebase_token
                    firebase_status = push_notification(message, title, token)
                except:
                    traceback.print_exc()

                # telegram notification for order received
                order_list_url = f'{request.scheme}://{request.get_host()}/dashboard/foors/orders/?token={get_room.room_token}&serialid={order.order_id}'
                message = f'You have received the order from room number {get_room.room_number}. View the indoor order list here: \n<a href="{order_list_url}">Click here</a>'
                # channel_name = 'Iberry2023'
                telegram_notification(get_room.user.channel_name, get_room.user.bot_token, message)
                
                return JsonResponse(
                    {
                        "success": "Order has been Placed.",
                        "room_id": get_room.room_token,
                        "order_id": order_id,
                    }
                )
            else:
                return JsonResponse(
                    {"error": "Cart is empty"}, status=status.HTTP_401_UNAUTHORIZED
                )
        except:
            traceback.print_exc()
            return JsonResponse(
                {"error": "Cart is empty"}, status=status.HTTP_401_UNAUTHORIZED
            )


class OrderStatusViewPage(TemplateView):
    template_name = "navs/order/order_status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_token = self.kwargs.get("room_token")
        order_id = self.kwargs.get("order_id")
        if room_token and order_id:
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                raise Http404("Order does not exist.")
        else:
            raise Http404("Order does not exist.")

        context["order"] = FoodOrdersSerializer(order).data

        return context


class OutdoorOrderStatusViewPage(TemplateView):
    template_name = "navs/order/outdoor_order_status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_token = self.kwargs.get("room_token")
        order_id = self.kwargs.get("order_id")
        if room_token and order_id:
            try:
                order = OutdoorOrder.objects.get(order_id=order_id)
            except OutdoorOrder.DoesNotExist:
                raise Http404("Order does not exist.")
        else:
            raise Http404("Order does not exist.")

        context['order'] = FoodOutdoorOrdersSerializer(order).data
        context['room_id'] = room_token
        return context


class QRCodeViewPage(TemplateView):
    template_name = "pages/phone.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("room_token")
        if pk:
            try:
                room = Room.objects.get(room_token=pk)
            except Room.DoesNotExist:
                raise Http404("Room does not exist.")
        else:
            raise Http404("Room does not exist.")

        get_dialers = Dialer.objects.filter(extension__user=room.user)
        context["dialers"] = PhoneDialerSerializer(get_dialers, many=True).data
        context["extension"] = ExtensionSerializer(room.extension).data

        return context


class ServicesPageView(TemplateView):
    template_name = "navs/service/services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("room_token")
        if pk:
            try:
                room = Room.objects.get(room_token=pk)
            except Room.DoesNotExist:
                raise Http404("Room does not exist.")
        else:
            raise Http404("Room does not exist.")

        get_services = Service.objects.filter(user=room.user)

        get_cart_items = ServiceCart.objects.filter(room=room)
        amounts = sum(item.service.price * 1 for item in get_cart_items)

        context["services"] = ServiceSerializer(get_services, many=True).data
        context["room_id"] = room.id
        context["cart_items"] = GetServiceCartSerializer(get_cart_items, many=True).data
        context["total_price"] = amounts
        return context


class ComplainCreateView(CreateView):
    permission_required = ""
    template_name = "navs/complain/complain.html"
    model = Complain
    form_class = ComplainForm

    def get_form_kwargs(self):
        kwargs = super(ComplainCreateView, self).get_form_kwargs()
        pk = self.kwargs.get("room_token")
        if pk:
            try:
                room = Room.objects.get(room_token=pk)
            except Room.DoesNotExist:
                raise Http404("Room does not exist.")
        else:
            raise Http404("Room does not exist.")
        kwargs["user"] = room.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # complain_id = self.kwargs.get("complain_id")
        pk = self.kwargs.get("room_token")
        if pk:
            try:
                room = Room.objects.get(room_token=pk)
            except Room.DoesNotExist:
                raise Http404("Room does not exist.")
        else:
            raise Http404("Room does not exist.")

        context["room_id"] = room.id
        return context

    def get_success_url(self):
        return reverse(
            "stores:complaint_detail",
            args=[self.object.room.room_token, self.object.complain_id],
        )


class ComplainDetailsView(TemplateView):
    template_name = "navs/complain/complain_status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_token = self.kwargs.get("room_token")
        complain_id = self.kwargs.get("complain_id")
        room = Room.objects.get(room_token=room_token)
        if room_token and complain_id:
            try:
                complain = Complain.objects.filter(complain_id=complain_id, status=0).order_by('-created_at')[0]
            except Complain.DoesNotExist:
                raise Http404("Complaint does not exist.")
        else:
            raise Http404("Complaint does not exist.")
        
        complaint_url = f'{self.request.scheme}://{self.request.get_host()}/dashboard/complaints/'
        message = f'You have received the complaint from {room_token}. View the complaint here: \n<a href="{complaint_url}">Click here</a>'
        telegram_notification(room.user.channel_name, room.user.bot_token, message)


        context["complain"] = ComplainSerializer(complain).data

        return context


"""
Service cart
"""


class ServiceCartModelView(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = ServiceCartSerializer

    def get_queryset(self):
        return ServiceCart.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        object_id = instance.id
        return object_id

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        get_qunatity = self.request.POST.get("qunatity")
        get_price = self.request.POST.get("price")
        room_id = self.request.POST.get("room")
        new_price = int(get_qunatity) * int(get_price)
        serializer.validated_data["price"] = new_price
        object_id = self.perform_create(serializer)
        room = Room.objects.get(id=room_id)
        cart_items = ServiceCart.objects.filter(room=room)
        amounts = sum(item.service.price * 1 for item in cart_items)

        extra_data = {
            "id": object_id,
            "total_price": amounts,
            "total_items": cart_items.count(),
        }

        return Response(extra_data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        cart_id = self.kwargs["pk"]
        instance = self.get_object()
        cart = ServiceCart.objects.get(id=cart_id)
        self.perform_destroy(instance)
        get_cart_items = ServiceCart.objects.filter(room=cart.room)
        amounts = sum(item.service.price * 1 for item in get_cart_items)
        response_data = {
            "total_price": amounts,
            "total_items": get_cart_items.count(),
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ServiceOrderPlaceAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = CustomOrderSerializer

    def post(self, request, format=None):
        serializer = CustomOrderSerializer(data=request.data)
        if serializer.is_valid():
            room = Room.objects.get(id=serializer.data["room"])
            cart_items = ServiceCart.objects.filter(room=room)
            if cart_items:
                order_id = str(uuid.uuid4().int & (10**8 - 1))
                order = ServiceOrder.objects.create(order_id=order_id, room=room)
                order.save()
                total_amount = 0
                for cart in cart_items:
                    service = cart.service
                    quantity = cart.quantity
                    total_amount += cart.service.price * quantity
                    order_service = ServiceOrderItem.objects.create(
                        order=order,
                        service=service,
                        quantity=quantity,
                        price=cart.price,
                    )
                    order.services.add(order_service)

                order.total_price = total_amount
                order.save()
                cart_items.delete()
                
                # Send push notification
                # registration_token = room.user.firebase_token
                # message = f'Order received from room number {room.room_number}'
                # notification = messaging.Notification(
                #     title=f'Order received from room number {room.room_number}',
                #     body=message,
                # )
                # message = messaging.Message(
                #     notification=notification,
                #     token=registration_token,
                # )
                # messaging.send(message)

                # # telegram notification for service received 
                service_url = f'{request.scheme}://{request.get_host()}/dashboard/services/orders/'
                message = f'You have received the service from {room.room_token}. View the service here: \n<a href="{service_url}">Click here</a>'
                telegram_notification(room.user.channel_name, room.user.bot_token, message)

                return Response(
                    {
                        "success": "Order has been Placed.",
                        "room_id": room.room_token,
                        "order_id": order_id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Cart is empty"}, status=status.HTTP_401_UNAUTHORIZED
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceOrderStatusViewPage(TemplateView):
    template_name = "navs/service/service_order_status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_token = self.kwargs.get("room_token")
        order_id = self.kwargs.get("order_id")
        if room_token and order_id:
            try:
                order = ServiceOrder.objects.get(order_id=order_id)
            except ServiceOrder.DoesNotExist:
                raise Http404("Order does not exist.")
        else:
            raise Http404("Order does not exist.")

        context["order"] = ServiceOrdersSerializer(order).data

        return context


class ServiceOrderModelView(viewsets.ModelViewSet):
    serializer_class = ServiceOrderSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return ServiceUpdateOrderSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        return ServiceOrder.objects.all()

def GlobalUpdateAPIView(request):
    if request.method == 'GET':
        try:
            config_value = request.GET.get('config_value').upper()
            if config_value == 'Y':
                Room.objects.filter(user=request.user).update(status=True)
            else:
                Room.objects.filter(user=request.user).update(status=False)
            
            # update the global
            Global.objects.filter(user=request.user).update(
              config_value=config_value
            )
            return JsonResponse({
                'status': True
            })
        except:
            return JsonResponse({
                'status': False
            })


def CheckConfigStoreToken(request, *args, **kwargs):
    if request.method == 'GET':
        try:
            room_token = kwargs.get('room_token')
            user = Room.objects.get(room_token=room_token).user
            global_conf = Global.objects.filter(user=user).first()
            if global_conf.config_value == 'Y':
                return render(request, 'navs/home/ask_user_token.html', {
                    'room_token': room_token
                })
            else:
                return redirect(reverse('stores:my_url', kwargs={
                    'room_token': room_token
                }))
        except:
            import traceback
            traceback.print_exc()

class ValidateConfigStoreToken(APIView):

    def post(self, request, **kwargs):
        try:
            room_token = kwargs.get('room_token')
            qr_room_token = request.data['qr_room_token']
            Room.objects.get(room_token=room_token, auth_token=qr_room_token)
            return Response({
                'status': True,
                'uri': f'{request.scheme}://{request.get_host()}/store/{room_token}/'
            })
        except Room.DoesNotExist:
            return Response({
                'status': False
            })



# contact us static page
def contact_us(request):
    room_id = request.GET.get('room_id')
    user = User.objects.filter(outdoor_token=room_id)[0]
    return render(request, 'navs/home/contact_us.html',{
        'address': user.address,
        'phone': user.phone,
        'email': user.email,
        'room_id': room_id,
        'user': user,
        'picture': user.picture.url
    })


def contact_send(request):
    try:
        if request.method == 'POST':
            # payloads = request.POST
            # payloads =  json.loads(request.body.decode('utf-8'))
            payloads = request.POST
            fullname = payloads.get('fullname', '')
            email = payloads.get('email', '')
            phone = payloads.get('phone', '')
            subject = payloads.get('subject', '')
            message = payloads.get('message', '')


            
            # room_id = payloads.get('room_id', '')
            # room_id = request.GET.get('room_id', '')

            # print(room_id)
            # token = User.objects.filter(outdoor_token=room_id)[0]

            # Send email
            send_mail(
                subject,
                f"From: {fullname}\nEmail: {email}\nPhone: {phone}\n\n{message}",
                email,  # Replace with your email address
                # [token.email],
                ['garimasachdeva25@gmail.com'],  # Replace with recipient email address
                fail_silently=False,
            )
            # print(token.email)
        #     send_mail("Subject", "text body", "raturi002@gmail.com",
        #   ["garimasachdeva25@gmail.com"], html_message="<html>html body</html>")

            # Return JSON response
            return JsonResponse({'message': 'Message sent successfully!'})
    except:
        traceback.print_exc()



# terms and condition static page
def terms_and_conditions(request):
    room_id = request.GET.get('room_id')
    user = User.objects.filter(outdoor_token=room_id)[0]
    terms = TermHeading.objects.get(user=user, page=0)
    sub_terms = SubHeading.objects.filter(main=terms)

    return render(request, 'navs/home/terms_conditions.html', {
        'main_title': terms.main_title,
        'main_content': terms.main_content,
        'sub_terms': sub_terms,
        'email': user.email,
        'address': user.address,
        'room_id': room_id,
        'user': user,
        'picture': user.picture.url
    })


# privacy policy static page
def privacy_policy(request):
    room_id = request.GET.get('room_id')
    user = User.objects.filter(outdoor_token=room_id)[0]
    terms = TermHeading.objects.get(user=user, page=1)
    sub_terms = SubHeading.objects.filter(main=terms)

    return render(request, 'navs/home/privacy_policy.html', {
        'main_title': terms.main_title,
        'main_content': terms.main_content,
        'sub_terms': sub_terms,
        'email': user.email,
        'address': user.address,
        'room_id': room_id,
        'user': user,
        'picture': user.picture.url
    })



# shipping policy static page 
def shipping_policy(request):
    room_id = request.GET.get('room_id')
    user = User.objects.filter(outdoor_token=room_id)[0]
    terms = TermHeading.objects.get(user=user, page=2)
    sub_terms = SubHeading.objects.filter(main=terms)

    return render(request, 'navs/home/shipping_policy.html', {
        'main_title': terms.main_title,
        'main_content': terms.main_content,
        'sub_terms': sub_terms,
        'email': user.email,
        'room_id': room_id,
        'user': user,
        'picture': user.picture.url
    })



# cancel refund static page
def cancel_refund(request):
    room_id = request.GET.get('room_id')
    user = User.objects.filter(outdoor_token=room_id)[0]
    terms = TermHeading.objects.get(user=user, page=3)
    sub_terms = SubHeading.objects.filter(main=terms)

    return render(request, 'navs/home/cancel_refund.html', {
        'main_title': terms.main_title,
        'main_content': terms.main_content,
        'sub_terms': sub_terms,
        'email': user.email,
        'room_id': room_id,
        'user': user,
        'picture': user.picture.url
    })



def render_logo(request):
    room_id = request.GET.get('room_id')
    if not room_id:
        return HttpResponseBadRequest("Room ID is missing in request parameters")

    # Retrieve the user with the specified picture (room_id)
    try:
        user = User.objects.get(picture=room_id)
    except User.DoesNotExist:
        return HttpResponseBadRequest("User with specified room_id does not exist")

    # Render the template with the user's picture
    return render(request, 'navs/includes/menu.html', {'picture': user.picture.url})



    # room_id = request.GET.get('room_id')
    # user = User.objects.filter(picture=room_id)[0]
    # return render(request, 'navs/includes/menu.html', {
    #     'picture': user.picture
    # })


def showFirebaseJS(request):
    data='importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");' \
         'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js"); ' \
         'var firebaseConfig = {' \
         '        apiKey: "AIzaSyB3YnNXnBSDkuJp3QZKYYgnM52Jwawipoc",' \
         '        authDomain: "iberry-81920.firebaseapp.com",' \
         '        databaseURL: "https://iberry-81920.firebaseio.com",' \
         '        projectId: "iberry-81920",' \
         '        storageBucket: "iberry-81920.appspot.com",' \
         '        messagingSenderId: "661156171796",' \
         '        appId: "1:661156171796:web:eabde955604c4b64bd9701",' \
         '        measurementId: "G-9M4YJQ5DLL"' \
         ' };' \
         'firebase.initializeApp(firebaseConfig);' \
         'const messaging=firebase.messaging();' \
         'messaging.setBackgroundMessageHandler(function (payload) {' \
         '    console.log(payload);' \
         '    const notification=JSON.parse(payload);' \
         '    const notificationOption={' \
         '        body:notification.body,' \
         '        icon:notification.icon' \
         '    };' \
         '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
         '});'

    return HttpResponse(data,content_type="text/javascript")




# pwa manifest
def manifestview(request):
    if request.method == 'GET':
        manifest = {
            "name": "iberry",
            "short_name": "iberry",
            "start_url": f"/store/{request.GET.get('token')}/foods/outdoor_items/",
            # "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#000000",
            "prefer_related_applications": True,
            "icons": [
                {
                    "src": "/static/images/iberry_logo.png",
                    "sizes": "320x320",
                    "type": "image/png"
                },
                {
                    "src": "/static/images/iberry512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                },
                {
                    "src": "/static/images/iberry192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "maskable"
                }
            ]
        }
        return JsonResponse(manifest)



