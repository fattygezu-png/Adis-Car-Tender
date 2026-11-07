from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Institution(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(
        upload_to='institution_logos/', blank=True, null=True
    )
    rules_pdf = models.FileField(
        upload_to='institution_rules/',
        blank=True,
        null=True,
        help_text='Upload official rules and regulations PDF file for this institution.',
    )
    deadline = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Deadline date and time when bidding closes.',
    )

    # Manual toggles for overall Institution status
    is_announced = models.BooleanField(
        default=False,
        help_text='Check to manually mark this institution tender as ANNOUNCED.',
    )
    is_dismissed = models.BooleanField(
        default=False,
        help_text='Check to manually mark this institution tender as DISMISSED / CANCELLED.',
    )

    def __str__(self):
        return self.name


class VehicleTender(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    make = models.CharField(max_length=100, blank=True, null=True)
    body_type = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    model_year = models.IntegerField(blank=True, null=True)
    starting_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    plate_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Enter plate number (accepts letters and numbers)',
    )

    image = models.ImageField(
        upload_to='tender_cars/', blank=True, null=True, help_text='Car picture'
    )

    winning_price = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    winner_name = models.CharField(max_length=200, blank=True, null=True)

    # Manual toggles for specific Vehicle Tender status
    is_announced = models.BooleanField(
        default=False,
        help_text='Check to mark this car tender as ANNOUNCED.',
    )
    is_dismissed = models.BooleanField(
        default=False,
        help_text='Check to mark this car tender as DISMISSED.',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} - {self.institution.name}'


class FavoriteInstitution(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite_institutions'
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'institution')


class FavoriteVehicleTender(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite_vehicles'
    )
    vehicle = models.ForeignKey(
        VehicleTender,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vehicle')