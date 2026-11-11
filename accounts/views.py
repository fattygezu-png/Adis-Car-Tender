from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .forms import CustomerRegistrationForm, ManualSubscriptionForm
from .models import CustomerSubscription, Notification

User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Ensure new users are active immediately
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Adis Car Tender.')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/')
        return redirect('user_dashboard')

    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')

        # Authenticate directly against database credentials
        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                if user.is_staff or user.is_superuser:
                    return redirect('/admin/')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'This account is currently inactive.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def user_dashboard(request):
    # Filter strictly by foreign key (user=request.user) to isolate records
    user_subscriptions = CustomerSubscription.objects.filter(user=request.user)

    # Fetch user notifications and unread count
    notifications = request.user.notifications.all()[:10]
    unread_count = request.user.notifications.filter(is_read=False).count()

    if request.method == 'POST':
        form = ManualSubscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.user = request.user  # Forcefully assign the authenticated User instance
            if not sub.sender_name:
                sub.sender_name = request.user.username
            sub.save()
            messages.success(
                request,
                'Subscription request submitted successfully! Waiting for admin approval.',
            )
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Please check your submission details.')
    else:
        form = ManualSubscriptionForm()

    context = {
        'subscriptions': user_subscriptions,
        'form': form,
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def mark_notifications_as_read(request):
    """Marks all unread notifications as read when the user opens the bell dropdown."""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid method'}, status=400)