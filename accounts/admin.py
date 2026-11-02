from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomerSubscription

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'phone_number',
        'is_staff',
        'is_superuser',
    )


@admin.action(description='Approve selected subscriptions')
def approve_subscriptions(modeladmin, request, queryset):
    queryset.update(status='APPROVED')


@admin.action(description='Reject selected subscriptions')
def reject_subscriptions(modeladmin, request, queryset):
    queryset.update(status='REJECTED')


@admin.action(description='Reset selected subscriptions to Pending')
def reset_subscriptions(modeladmin, request, queryset):
    queryset.update(status='PENDING')


@admin.register(CustomerSubscription)
class CustomerSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'sender_name',
        'plan',
        'payment_method',
        'status',
        'created_at',
    )
    list_filter = ('plan', 'status', 'payment_method')
    search_fields = ('sender_name', 'user__username')
    actions = [
        approve_subscriptions,
        reject_subscriptions,
        reset_subscriptions,
    ]