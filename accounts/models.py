from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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

    def get_expiry_date(self):
        if self.created_at:
            if 'Monthly' in self.plan_name:
                days = 30
            elif 'Quarterly' in self.plan_name:
                days = 90
            elif 'Semiannually' in self.plan_name or 'Semi-Annually' in self.plan_name:
                days = 180
            else:
                days = 30
            return self.created_at + timedelta(days=days)
        return None

    def days_remaining(self):
        expiry = self.get_expiry_date()
        if expiry:
            delta = expiry - timezone.now()
            return max(0, delta.days)
        return 0

    def is_expired(self):
        expiry = self.get_expiry_date()
        if expiry:
            return timezone.now() > expiry
        return False

    def is_active(self):
        return str(self.status).upper() == 'APPROVED' and not self.is_expired()

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Automatically prune older notifications, keeping only the latest 20 per user
        excess_notifications = Notification.objects.filter(user=self.user).order_by('-created_at')[20:]
        if excess_notifications.exists():
            Notification.objects.filter(id__in=excess_notifications.values('id')).delete()