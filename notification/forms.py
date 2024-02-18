from django import forms
from notification.models import Notification

class NotificationForm(forms.ModelForm):
    
    class Meta:
        model = Notification
        widgets = {
            "room": forms.Select(attrs={'class': 'form-select'}),
            "notification_type": forms.Select(attrs={'class': 'form-select'}),
            "title": forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter Title"}),
            "description": forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Enter Description"}),
        }
        fields = "__all__"