from django.db.models import Q
from .models import CustomerSubscription, Notification


def subscription_status(request):
    """Passes detailed subscription and approval state to templates."""
    if request.user.is_authenticated:
        # Check if user has an explicitly APPROVED subscription
        is_approved = CustomerSubscription.objects.filter(
            Q(user=request.user)
            | Q(sender_name__iexact=request.user.username.strip()),
            status__iexact='APPROVED',
        ).exists()

        # Check latest subscription status
        latest_sub = (
            CustomerSubscription.objects.filter(
                Q(user=request.user)
                | Q(sender_name__iexact=request.user.username.strip())
            )
            .order_by('-created_at')
            .first()
        )

        is_rejected = (
            latest_sub and latest_sub.status.upper().strip() == 'REJECTED'
        )
        is_pending = (
            latest_sub and latest_sub.status.upper().strip() == 'PENDING'
        )

        return {
            'is_approved_user': True,  # Forced to True so all authenticated users see navigation items
            'is_rejected_user': is_rejected,
            'is_pending_user': is_pending,
            'latest_subscription': latest_sub,
        }

    return {
        'is_approved_user': False,
        'is_rejected_user': False,
        'is_pending_user': False,
        'latest_subscription': None,
    }


def notification_processor(request):
    """Passes user notifications and unread count to all templates globally."""
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        unread_count = notifications.filter(is_read=False).count()
        return {
            'global_notifications': notifications,
            'global_unread_count': unread_count,
        }
    return {
        'global_notifications': [],
        'global_unread_count': 0,
    }