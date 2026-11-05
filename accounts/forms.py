from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, CustomerSubscription


class CustomerRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-sm text-gray-900 transition-all',
            'placeholder': 'Enter phone number'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('phone_number',) # Email removed
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-sm text-gray-900 transition-all',
                'placeholder': 'Enter username'
            }),
        }


class ManualSubscriptionForm(forms.ModelForm):
    class Meta:
        model = CustomerSubscription
        fields = ['plan_name', 'payment_method', 'sender_name']
        widgets = {
            'plan_name': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-sm text-gray-900 transition-all'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-sm text-gray-900 transition-all'
            }),
            'sender_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-sm text-gray-900 transition-all',
                'placeholder': 'Enter full sender name or Txn ID'
            }),
        }