from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from .forms import CustomerRegistrationForm, ManualSubscriptionForm
from .models import CustomerSubscription

User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('user_dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Check if user is staff or superuser, and redirect accordingly
            if user.is_staff or user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('user_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def user_dashboard(request):
    # Filter strictly by foreign key (user=request.user) to isolate records
    user_subscriptions = CustomerSubscription.objects.filter(user=request.user)

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
        form = ManualSubscriptionForm()

    context = {
        'subscriptions': user_subscriptions,
        'form': form,
    }
    return render(request, 'accounts/dashboard.html', context)