from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import Notification
from .models import Institution

User = get_user_model()


@receiver(post_save, sender=Institution)
def institution_notification_handler(sender, instance, created, **kwargs):
    """Trigger notifications at the Institution level for new tenders, winners, and dismissals."""
    users = User.objects.filter(is_active=True)
    
    # 1. New Institution Tender Notification: Fires automatically when a new institution is registered
    if created:
        tender_title = "New Institution Tender Available!"
        tender_msg = f"A new institution tender for '{instance.name}' has been posted. Check out the available vehicles!"
        
        for user in users:
            exists = Notification.objects.filter(user=user, title=tender_title, message=tender_msg).exists()
            if not exists:
                Notification.objects.create(
                    user=user,
                    title=tender_title,
                    message=tender_msg
                )

    # 2. Institution Winner Announcement: Fires when admin checks 'is_announced' on the institution
    if instance.is_announced:
        winner_title = "Institution Winners Announced!"
        winner_msg = f"The winner announcement archive for '{instance.name}' has now been published."
        
        for user in users:
            exists = Notification.objects.filter(user=user, title=winner_title, message=winner_msg).exists()
            if not exists:
                Notification.objects.create(
                    user=user,
                    title=winner_title,
                    message=winner_msg
                )

    # 3. Institution Dismissed Notification: Fires when admin checks 'is_dismissed' on the institution
    if instance.is_dismissed:
        dismiss_title = "Institution Tender Dismissed"
        dismiss_msg = f"The institution tender for '{instance.name}' has been dismissed or cancelled."
        
        for user in users:
            exists = Notification.objects.filter(user=user, title=dismiss_title, message=dismiss_msg).exists()
            if not exists:
                Notification.objects.create(
                    user=user,
                    title=dismiss_title,
                    message=dismiss_msg
                )