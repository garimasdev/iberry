from django import forms
from django.forms import ModelForm

from dashboard.models import Complain, ComplainType, Dialer, Extension, Janus, Pbx, Room, Service, Table
from dashboard.serializers import PriceSerializer
from stores.models import Category, Item, Price, SubCategory



"""
Room Form
"""
# room create form
class RoomForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RoomForm, self).__init__(*args, **kwargs)
        self.fields['extension'].queryset = Extension.objects.filter(user=user)
        
        
    class Meta:
        model = Room
        fields = "__all__"

    class Meta:
        model = Room
        fields = ['room_number', 'extension', 'status']
        widgets = {
            "room_number": forms.TextInput(attrs={'class': 'form-select', 'placeholder': 'Enter Room Number', 'autofocus': True},),
            "extension": forms.Select(attrs={'class': 'form-select',},),
            "status": forms.CheckboxInput(attrs={'class': 'form-check-input mt-0', 'hidden': True},),
        }
        

# Update room form
class RoomUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RoomUpdateForm, self).__init__(*args, **kwargs)
        self.fields['extension'].queryset = Extension.objects.filter(user=user)
        
        
    class Meta:
        model = Room
        fields = ['room_number', 'extension', 'status']
        widgets = {
            "room_number": forms.TextInput(attrs={'class': 'form-select', 'placeholder': 'Enter Room Number', 'autofocus': True},),
            "extension": forms.Select(attrs={'class': 'form-select',},),
            "status": forms.CheckboxInput(attrs={'class': 'form-check-input mt-0', 'hidden': True},),
        }


"""
Table Form
"""
# New table form
class TableForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TableForm, self).__init__(*args, **kwargs)
        
        
    class Meta:
        model = Table
        fields = "__all__"
        widgets = {
            "table_number": forms.TextInput(attrs={'class': 'form-select', 'placeholder': 'Enter Table Number', 'autofocus': True},),
            "status": forms.CheckboxInput(attrs={'class': 'form-check-input mt-0'}),
        }


# update table form
class TableUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TableUpdateForm, self).__init__(*args, **kwargs)
        
        
    class Meta:
        model = Table
        fields = ['table_number', 'status']
        widgets = {
            "table_number": forms.TextInput(attrs={'class': 'form-select', 'placeholder': 'Enter Table Number', 'autofocus': True},),
            "status": forms.CheckboxInput(attrs={'class': 'form-check-input mt-0', 'hidden': True}),
        }


"""
Foods Form
"""
class FoodsItemForm(ModelForm):
    get_prices = forms.JSONField(required=False)
    
    def __init__(self, *args, **kwargs):
        # instance = kwargs.pop('instance')
        user = kwargs.pop('user')
        super(FoodsItemForm, self).__init__(*args, **kwargs)
        self.fields['get_prices'].label = 'Get Prices'
        get_instance = kwargs.pop('instance')
        
        get_category = Category.objects.filter(user=user)
        self.fields['category'].queryset = get_category
        self.fields['prices'].queryset = Price.objects.all()
        # self.fields['sub_category'].queryset = SubCategory.objects.filter(category=get_category)
        if get_instance:
            self.fields['get_prices'].initial = PriceSerializer(get_instance.prices, many=True).data
    
        
    class Meta:
        model = Item
        fields = "__all__"
        widgets = {
            "item_type": forms.Select(attrs={'class': 'form-select'}),
            "category": forms.Select(attrs={'class': 'form-select', 'required': True}),
            "sub_category": forms.Select(attrs={'class': 'form-select', 'disabled': True}),
            "title": forms.TextInput(attrs={'class': 'form-select', 'required': True}),
            "image": forms.FileInput(attrs={'class': 'form-select', 'accept': 'image/*'}),
            # 'prices': forms.Select(attrs={'class': 'form-select', 'required': True, 'multiple': True}),
            # "prices": forms.NumberInput(attrs={'class': 'form-select', 'required': True}),
            "quantity": forms.NumberInput(attrs={'class': 'form-select'}),
            "description": forms.Textarea(attrs={'class': 'form-select'}),
            "tax_rate": forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        image_field = cleaned_data.get('image')
        if not image_field:
            cleaned_data['image'] = self.instance.image
        return cleaned_data
        
        
        
class FoodsCategoryForm(ModelForm):    
    class Meta:
        model = Category
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-select', 'autofocus':'autofocus'}),
        }


class SubCategoryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(SubCategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        
    class Meta:
        model = SubCategory
        fields = "__all__"
        widgets = {
            "category": forms.Select(attrs={'class': 'form-select'},),
            "name": forms.TextInput(attrs={'class': 'form-select', 'autofocus':'autofocus'}),
        }
        
        

class ExtensionForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ExtensionForm, self).__init__(*args, **kwargs)
        self.fields['pbx'].queryset = Pbx.objects.filter(user=user)
        self.fields['janus'].queryset = Janus.objects.filter(user=user)
        
        
    class Meta:
        model = Extension
        fields = "__all__"
        widgets = {
            "extension_name": forms.TextInput(attrs={'class': 'form-control', 'autofocus':'autofocus'}),
            "extension_sip_number": forms.TextInput(attrs={'class': 'form-select',}),
            "extension_sip_password": forms.TextInput(attrs={'class': 'form-select',}),
            "pbx": forms.Select(attrs={'class': 'form-select'},),
            "janus": forms.Select(attrs={'class': 'form-select',},),
        }
        
        

class PbxForm(ModelForm):
    class Meta:
        model = Pbx
        fields = "__all__"
        widgets = {
            "pbx_name": forms.TextInput(attrs={'class': 'form-select', 'placeholder': 'Enter Name', 'autofocus': True},),
            "pbx_domain": forms.TextInput(attrs={'class': 'form-select', 'placeholder': "Enter Domain/IP Address"},),
        }
        
        
class JanusForm(ModelForm):
    class Meta:
        model = Janus
        fields = "__all__"
        widgets = {
            "janus_name": forms.TextInput(attrs={'class': 'form-select', 'placeholder': 'Enter Name', 'autofocus': True},),
            "janus_domain": forms.TextInput(attrs={'class': 'form-select', 'placeholder': "Enter Domain/IP Address"},),
        }
        


class ServiceForm(ModelForm):        
    class Meta:
        model = Service
        fields = "__all__"
        widgets = {
            "image": forms.FileInput(attrs={'class': 'form-select', 'accept': 'image/*', 'required': True}),
            "name": forms.TextInput(attrs={'class': 'form-select', 'required': True}),
            "price": forms.NumberInput(attrs={'class': 'form-select', 'required': True}),
            "quantity": forms.NumberInput(attrs={'class': 'form-select', 'required': True}),
            "description": forms.Textarea(attrs={'class': 'form-select', 'required': True})
        }


class ComplainForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ComplainForm, self).__init__(*args, **kwargs)
        self.fields['complain'].queryset = ComplainType.objects.filter(user=user)
        
    class Meta:
        model = Complain
        fields = "__all__"
        widgets = {
            "complain": forms.Select(attrs={'class': 'form-select', 'required': True}),
            "report": forms.Textarea(attrs={'class': 'form-select'})
        }
        

class ComplainTypeForm(ModelForm):    
    class Meta:
        model = ComplainType
        fields = "__all__"
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-select', 'required': True})
        }




class DialerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(DialerForm, self).__init__(*args, **kwargs)
        self.fields['extension'].queryset = Extension.objects.filter(user=user)
     
        
    class Meta:
        model = Dialer
        fields = "__all__"
        widgets = {
            "c2c_name": forms.TextInput(attrs={'class': 'form-select', 'placeholder': 'Enter Dialer Option Label'},),
            "extension": forms.Select(attrs={'class': 'form-select'},),
            "status": forms.CheckboxInput(attrs={'class': 'form-check-input mt-0', 'hidden': True},),
        }
                

# class OdooForm(forms.ModelForm):    
#     class Meta:
#         model = OdooUser
#         widgets = {
#         'password': forms.PasswordInput(),
#        }
#         fields = '__all__'
        
# # Existing User Id Form
# class UserIdForm(forms.ModelForm):
#     "This modelForm for styling the user id form"
    
#     class Meta:
#         model = ExistingUser
#         fields = "__all__"
#         widgets = {
#             "user": forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select User'},),
#             "exg_user_id": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter user id",}),
#             "user_type": forms.NumberInput(attrs={'class': 'form-select'}),
#             # "is_used": forms.BooleanField(attrs={'class': 'form-control'}),
#         }
        
        
# class UserForm(forms.ModelForm):
#     "This modelForm for styling the user form"
    
#     class Meta:
#         model = User
#         # fields = ("account_group",'birthday','blood_group','email','father_name','gender',)
#         fields = ("account_group","birthday","blood_group","email","family_income","father_name","father_profession","gender","guardian_name","guardian_phone_number",
#               "mother_name","name","permanent_address", "phone_number","picture", "present_address","religion","subject","user_id","user_type")
#         widgets = {
#             "account_group": forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select Account Group'},),
#             "birthday": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "yyyy-mm-dd",}),
#             "blood_group": forms.Select(attrs={'class': 'form-select'}),
#             "email": forms.TextInput(attrs={'class': 'form-control', 'readonly':True}),
#             "family_income": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Enter family income"}),
#             "father_name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter father name"}),
#             "father_profession": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter father profession"}),
#             "gender": forms.Select(attrs={'class': 'form-select'}),
#             "guardian_name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter guardian name"}),
#             "guardian_phone_number": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter guardian phone number"}),
#             "mother_name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter mother name"}),
#             "name": forms.TextInput(attrs={'class': 'form-control', 'required': True}),
#             "permanent_address": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter permanent address"}), 
#             "phone_number": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "+88017777777777",}),
#             # "picture": forms.FileInput(attrs={'class': 'form-control'}), 
#             "present_address": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter present address"}),
#             "religion": forms.Select(attrs={'class': 'form-select'}),
#             "subject": forms.Select(attrs={'class': 'form-select', 'placeholder': 'Enter subject name'},),
#             "user_id": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter user id", 'readonly':True}),
#             "user_type": forms.Select(attrs={'class': 'form-select'})
#         }
        