from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


class CustomerSubscription(models.Model):
    PAYMENT_CHOICES = [
        ('CBE', 'Commercial Bank of Ethiopia (1000572034556 - feyo gezu)'),
        ('TELEBIRR', 'Telebirr (0930771571 - feyo gezu)'),
        ('AWASH', 'Awash Bank (01339367484 - feyo gezu)'),
    ]

    PLAN_CHOICES = [
        ('Monthly (500 ETB)', 'Monthly Plan — 500 ETB'),
        ('Quarterly (1300 ETB)', 'Quarterly Plan — 1300 ETB'),
        ('Semiannually (2400 ETB)', 'Semi-Annually Plan — 2400 ETB'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        null=True,
        blank=True,
    )
    plan_name = models.CharField(
        max_length=100, choices=PLAN_CHOICES, default='Monthly (500 ETB)'
    )
    sender_name = models.CharField(max_length=100)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_CHOICES, default='TELEBIRR'
    )
    status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return str(self.status).upper() == 'APPROVED'

    def __str__(self):
        return f'{self.sender_name} ({self.user}) - {self.plan_name} via {self.payment_method} [{self.status}]'


class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"