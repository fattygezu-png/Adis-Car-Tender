from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def subscription_required(view_func):
    """Ensures only active subscribed users can view tender details."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_subscribed:
            return view_func(request, *args, **kwargs)
        messages.warning(request, "You need an active subscription to access tender listings.")
        return redirect('subscribe')
    return _wrapped_view