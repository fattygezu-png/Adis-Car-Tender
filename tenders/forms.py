from django import forms
from django.core.exceptions import ValidationError
from .models import VehicleTender

class VehicleTenderAdminForm(forms.ModelForm):
    class Meta:
        model = VehicleTender
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        is_announced = cleaned_data.get('is_winner_announced')
        winning_price = cleaned_data.get('winning_price')

        if is_announced and not winning_price:
            raise ValidationError({
                'winning_price': "You must enter a winning price when announcing a winner."
            })
        return cleaned_data