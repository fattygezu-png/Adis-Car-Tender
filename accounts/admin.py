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

    # Adds phone_number to the detail edit form (Change user page)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('phone_number',)}),
    )

    # Adds phone_number when creating a new user inside Django admin
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('phone_number',)}),
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
        'plan_name',
        'payment_method',
        'status',
        'created_at',
    )
    list_filter = ('plan_name', 'status', 'payment_method')
    search_fields = ('sender_name', 'user__username')
    actions = [
        approve_subscriptions,
        reject_subscriptions,
        reset_subscriptions,
    ]