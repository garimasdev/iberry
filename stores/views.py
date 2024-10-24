from encodings import utf_8_sig
from inspect import trace
import json
import os
import string
import random
import traceback
from dashboard.models import Global
import uuid
from django.http import HttpResponseBadRequest


from django.core.mail import send_mail

import razorpay
from accounts.models import User
from django.shortcuts import render
import firebase_admin
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
from firebase_admin import credentials, messaging
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


import sys
if sys.platform == 'linux':
    import telegram
    from telegram import ParseMode

# from notification.helpers import telegram_notification


credentials_path = os.path.join(settings.BASE_DIR, "stores", "credentials.json")
# Initialize Firebase Admin SDK
cred = credentials.Certificate(credentials_path)
firebase_admin.initialize_app(cred)


# Create your views here.
def showFirebaseJS(request):
    file_path = os.path.join(
        settings.BASE_DIR, "static", "js", "firebase-messaging-sw.js"
    )
    with open(file_path, "r") as file:
        js_content = file.read()

    return HttpResponse(js_content, content_type="application/javascript")


class NotFoundPageView(TemplateView):
    template_name = "pages/page-404.html"


class ModulesViewPage(TemplateView):
    template_name = "modules/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def filterItemByCategories(
    user, categories=None, sub_category=None, item_type=None, search=None
):
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
        amounts = sum(item.price * item.quantity for item in get_cart_items)
        context["categories"] = FoodCategoriesSerializer(
            get_categories.exclude(name__in=["Bar", "Veg", "Non Veg"]), many=True
        ).data
        context["sub_categories"] = FoodSubCategoriesSerializer(
            get_sub_category, many=True
        ).data
        context["items"] = items
        context["room_id"] = room.id
        context["cart_items"] = CartItemSerializer(get_cart_items, many=True).data
        context["total_price"] = amounts
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
                    self.request.session['anonymous_user_id'] = ''.join(random.choices(string.ascii_uppercase+string.digits, k=12))
                    temp_user_id = Temporary_Users.objects.create(
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
            amounts = sum(item.price * item.quantity for item in get_cart_items)
            context["categories"] = FoodCategoriesSerializer(
                get_categories.exclude(name__in=["Bar", "Veg", "Non Veg"]), many=True
            ).data
            context["sub_categories"] = FoodSubCategoriesSerializer(
                get_sub_category, many=True
            ).data
            outdoor_token = User.objects.get(outdoor_token=pk)
            context['phone'] = outdoor_token.phone
            context["items"] = items
            context["room_id"] = pk
            context["cart_items"] = OutdoorCartItemSerializer(get_cart_items, many=True).data
            context["total_price"] = amounts
            context['logo'] = room.picture.url
            context['hotel_name'] = room.username
            context["anonymous_user_id"] = temp_user_id.anonymous_user_id
            context["razorpay_clientid"] = room.razorpay_clientid
            context["razorpay_clientsecret"] = room.razorpay_clientsecret
            return context
        except:
            import traceback
            traceback.print_exc()


def CreatePaymentOrder(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            razorpay_clientid = request.GET.get('cid')
            razorpay_clientsecret = request.GET.get('secret')
            cart_items = OutdoorCart.objects.filter(anonymous_user_id=payload['anonymous_user_id'])
            cart_total = sum([item.quantity * item.price for item in cart_items])
            receipt = ''.join(random.choices(string.ascii_letters+string.digits, k=16))
            client = razorpay.Client(auth=(razorpay_clientid, razorpay_clientsecret))
            order_payload = {
                "amount": cart_total * 100,
                "currency": "INR",
                "receipt": receipt
            }
            order_response = client.order.create(data=order_payload)
            import traceback
            if 'id' not in order_response:
                return JsonResponse({
                    'status': False,
                    'traceback': json.dumps(traceback.format_exc())
                })
            # update the temp_users table with order id and receipt
            temp_user = Temporary_Users.objects.get(anonymous_user_id=payload['anonymous_user_id'])
            temp_user.razorpay_order_id = order_response['id']
            temp_user.receipt = receipt
            temp_user.order_total = str(cart_total * 100)
            temp_user.customer_name = payload['username']
            temp_user.customer_email = payload['email']
            temp_user.customer_phone = payload['phone']
            temp_user.customer_address = payload['address']
            temp_user.save()
            
            return JsonResponse({
                'status': True,
                'uri': f'{request.scheme}://{request.get_host()}/payment/checkout?user_id={payload["anonymous_user_id"]}&user={payload["user"]}'
            })
        except:
            import traceback
            return JsonResponse({
                'status': False,
                'traceback': json.dumps(traceback.format_exc())
            })


def paymentCheckout(request):
    if request.method == 'GET':
        anonymous_user_id = request.GET.get('user_id')
        user_token = request.GET.get('user')
        user = User.objects.get(outdoor_token=user_token)
        temp_user = Temporary_Users.objects.get(anonymous_user_id=anonymous_user_id)
        return render(request, 'navs/home/checkout.html', {
            'key_id': user.razorpay_clientid,
            'amount': int(temp_user.order_total),
            'order_id': temp_user.razorpay_order_id,
            'phone': temp_user.customer_phone,
            'email': temp_user.customer_email,
            'name': temp_user.customer_name,
            # 'picture': user.picture.url,
            # 'company_name': user.name.capitalize(),
            'user_id': anonymous_user_id,
            'user_token': user_token
        })


@csrf_exempt
def paymentCheckoutSuccess(request):
    if request.method == 'POST':
        try:
            payload = request.POST
            get_room = User.objects.get(outdoor_token=request.GET.get('token'))
            client = razorpay.Client(auth=(get_room.razorpay_clientid, get_room.razorpay_clientsecret))
            status = client.utility.verify_payment_signature({
                'razorpay_order_id': payload['razorpay_order_id'],
                'razorpay_payment_id': payload['razorpay_payment_id'],
                'razorpay_signature': payload['razorpay_signature']
            })
            if status is True:
                cart_items = OutdoorCart.objects.filter(user=get_room, anonymous_user_id=request.GET.get('user_id'))
                if cart_items:
                    order_id = str(uuid.uuid4().int & (10**8 - 1))
                    order = OutdoorOrder.objects.create(order_id=order_id, user=get_room)
                    total_amount = 0
                    for cart in cart_items:
                        item = cart.item
                        quantity = cart.quantity
                        total_amount += cart.price * quantity
                        order_item = OutdoorOrderItem.objects.create(
                            order=order, item=item, quantity=quantity, price=cart.price
                        )
                        order.items.add(order_item)

                    order.total_price = total_amount
                    order.save()
                    cart_items.delete()
                    # here i can associate the order_id in temp_users
                    temp_user = Temporary_Users.objects.get(anonymous_user_id=request.GET.get('user_id'))
                    temp_user.custom_order_id = order_id
                    temp_user.save()
                    # Send push notification
                    message = f'A new order received'
                    notification = messaging.Notification(
                        title=f'A new order received',
                        body=message,
                    )
                    message = messaging.Message(
                        notification=notification,
                        token=get_room.firebase_token
                    )
                    messaging.send(message)
                    # telegram notification for order received
                    order_list_url = f'{request.scheme}://{request.get_host()}/dashboard/foods/outdoor-orders/'
                    message = f'You have received an order. View the order list here: \n<a href="{order_list_url}">Click here</a>'
                    telegram_notification(get_room.channel_name, message)                    
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
            get_room = User.objects.get(outdoor_token=request.GET.get('token'))
            cart_items = OutdoorCart.objects.filter(user=get_room, anonymous_user_id=request.GET.get('user_id'))
            cart_items.delete()
            return redirect(reverse('stores:foods-outdoor-items', kwargs={
                'room_token': request.GET.get('token')
            }))


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
        cart_items = Cart.objects.filter(room=room)

        total_items = sum(item.quantity for item in cart_items)
        amounts = sum(item.price * item.quantity for item in cart_items)
        extra_data = {
            "id": object_id,
            "total_price": amounts,
            "total_items": total_items,
        }

        return Response(extra_data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        cart_id = self.kwargs["pk"]
        instance = self.get_object()
        cart = Cart.objects.get(id=cart_id)
        self.perform_destroy(instance)
        get_cart_items = Cart.objects.filter(room=cart.room)
        amounts = sum(item.price * item.quantity for item in get_cart_items)
        total_items = sum(item.quantity for item in get_cart_items)
        response_data = {
            "total_price": amounts,
            "total_items": total_items,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class OutdoorCartModelView(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = OutdoorCartSerializer

    def get_queryset(self):
        room_id = self.request.query_params.get("room_id")
        if room_id:
            return OutdoorCart.objects.filter(user__outdoor_token=room_id)
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
            cart_items = OutdoorCart.objects.filter(user=user, anonymous_user_id=request.data['anonymous_user_id'])
            total_items = sum(item.quantity for item in cart_items)
            amounts = sum(item.price * item.quantity for item in cart_items)
            extra_data = {
                "id": object_id,
                "total_price": amounts,
                "total_items": total_items,
            }

            return Response(extra_data, status=status.HTTP_201_CREATED)
        except:
            import traceback
            traceback.print_exc()

    def destroy(self, request, *args, **kwargs):
        cart_id = self.kwargs["pk"]
        instance = self.get_object()
        cart = OutdoorCart.objects.get(id=cart_id)
        self.perform_destroy(instance)
        get_cart_items = OutdoorCart.objects.filter(user=cart.user)
        amounts = sum(item.price * item.quantity for item in get_cart_items)
        total_items = sum(item.quantity for item in get_cart_items)
        response_data = {
            "total_price": amounts,
            "total_items": total_items,
        }
        return Response(response_data, status=status.HTTP_200_OK)


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
                for cart in cart_items:
                    item = cart.item
                    quantity = cart.quantity
                    total_amount += cart.price * quantity
                    order_item = OutdoorOrderItem.objects.create(
                        order=order, item=item, quantity=quantity, price=cart.price
                    )
                    order.items.add(order_item)

                order.total_price = total_amount
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
                # Send push notification
                message = f'A new order received'
                notification = messaging.Notification(
                    title=f'A new order received',
                    body=message,
                )
                message = messaging.Message(
                    notification=notification,
                    token=get_room.firebase_token
                )
                messaging.send(message)
                order_list_url = f'{request.scheme}://{request.get_host()}/dashboard/foods/outdoor-orders/'
                message = f'You have received an order. View the order list here: \n<a href="{order_list_url}">Click here</a>'
                bot = telegram.Bot(token=settings.TELEGRAM['bot_token'])
                bot.send_message(chat_id=f'@{get_room.channel_name}', text=message, parse_mode=ParseMode.HTML)
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
            return Response({
                'success': "Order not being placed."
            })


@csrf_exempt
def PlaceOrderAPIView(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            serializer = CustomOrderSerializer(data=data)
            if serializer.is_valid():
                get_room = Room.objects.get(id=serializer.data["room"])
                cart_items = Cart.objects.filter(room=get_room)
                if cart_items:
                    order_id = str(uuid.uuid4().int & (10**8 - 1))
                    order = Order.objects.create(order_id=order_id, room=get_room)
                    order.save()
                    total_amount = 0
                    for cart in cart_items:
                        item = cart.item
                        quantity = cart.quantity
                        total_amount += cart.price * quantity
                        order_item = OrderItem.objects.create(
                            order=order, item=item, quantity=quantity, price=cart.price
                        )
                        order.items.add(order_item)

                    order.total_price = total_amount
                    order.save()
                    cart_items.delete()
                    # Send push notification
                    registration_token = get_room.user.firebase_token
                    message = f'Order received from room number {get_room.room_number}'
                    notification = messaging.Notification(
                        title=f'Order received from room number {get_room.room_number}',
                        body=message,
                    )
                    message = messaging.Message(
                        notification=notification,
                        token=registration_token,
                    )
                    messaging.send(message)
                    # telegram notification for order received
                    order_list_url = f'{request.scheme}://{request.get_host()}/dashboard/foors/orders/?token={get_room.room_token}&serialid={order.order_id}'
                    message = f'You have received the order from {get_room.room_number}. View the order list here: \n<a href="{order_list_url}">Click here</a>'
                    telegram_notification(get_room.user.channel_name, message)
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
        print(room_token)
        complain_id = self.kwargs.get("complain_id")
        print(complain_id)
        room = Room.objects.get(room_token=room_token)
        if room_token and complain_id:
            print("if case")
            try:
                print("try")

                complain = Complain.objects.filter(complain_id=complain_id, status=0).order_by('-created_at')[0]
                print("try case complain")
            except Complain.DoesNotExist:
                print("exception")
                raise Http404("Complaint does not exist.")
        else:
            print("else case")
            raise Http404("Complaint does not exist.")
        
        print("complaint generated")
        complaint_url = f'{self.request.scheme}://{self.request.get_host()}/dashboard/complaints/'
        print(complaint_url)
        message = f'You have received the complaint from {room_token}. View the complaint here: \n<a href="{complaint_url}">Click here</a>'
        print(message)
        telegram_notification(room.user.channel_name, message)


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
        print(get_qunatity)
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

                # telegram notification for service received 
                service_url = f'{request.scheme}://{request.get_host()}/dashboard/services/orders/'
                message = f'You have received the service from {room.room_token}. View the service here: \n<a href="{service_url}">Click here</a>'
                telegram_notification(room.user.channel_name, message)
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
        'room_id': room_id
    })


def contact_send(request):
    try:
        if request.method == 'POST':
            # payloads = request.POST
            # payloads =  json.loads(request.body.decode('utf-8'))
            payloads = request.POST
            print(payloads)
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
    return render(request, 'navs/home/terms_conditions.html', {
        'email': user.email,
        'room_id': room_id
    })


# shipping policy static page 
def shipping_policy(request):
    room_id = request.GET.get('room_id')
    user = User.objects.filter(outdoor_token=room_id)[0]
    return render(request, 'navs/home/shipping_policy.html', {
        'email': user.email,
        'room_id': room_id
    })


# privacy policy static page
def privacy_policy(request):
    room_id = request.GET.get('room_id')
    user = User.objects.filter(outdoor_token=room_id)[0]
    return render(request, 'navs/home/privacy_policy.html', {
        'email': user.email,
        'room_id': room_id
    })


# cancel refund static page
def cancel_refund(request):
    room_id = request.GET.get('room_id')
    user = User.objects.filter(outdoor_token=room_id)[0]
    return render(request, 'navs/home/cancel_refund.html', {
        'email': user.email,
        'room_id': room_id
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
            "icons": [
                {
                    "src": "/static/images/iberry_logo.png",
                    "sizes": "320x200",
                    "type": "image/png"
                }
            ]
        }
        return JsonResponse(manifest)



