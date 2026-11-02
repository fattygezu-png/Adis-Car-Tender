from django.shortcuts import redirect

def subscription_required(view_func):
    def wrapper(request, *args, **kwargs):
        # 1. Check if user is logged in at all
        if not request.user.is_authenticated:
            return redirect('login') # Adjust to your login URL name
            
        # 2. Check if the logged-in user has an active subscription
        if getattr(request.user, 'is_subscribed', False):
            return view_func(request, *args, **kwargs)
            
        # 3. If logged in but not subscribed, send to subscription page
        return redirect('subscribe_page') 
        
    return wrapper
