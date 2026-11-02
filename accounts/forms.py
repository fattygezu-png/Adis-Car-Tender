from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerSubscription

User = get_user_model()


class CustomerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class ManualSubscriptionForm(forms.ModelForm):
    class Meta:
        model = CustomerSubscription
        fields = ('plan', 'payment_method', 'sender_name')
        widgets = {
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'sender_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Name registered on payment account',
                }
            ),
        }