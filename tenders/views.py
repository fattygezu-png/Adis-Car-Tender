from accounts.models import CustomerSubscription
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import (
    FavoriteInstitution,
    FavoriteVehicleTender,
    Institution,
    VehicleTender,
)


def has_approved_subscription(user):
    """Checks whether the logged-in user has an approved active subscription."""
    if not user.is_authenticated:
        return False
    
    if user.is_staff or user.is_superuser:
        return True

    return CustomerSubscription.objects.filter(
        Q(user=user) | Q(sender_name__iexact=user.username.strip()),
        status__iexact='APPROVED',
    ).exists()


def get_dynamic_filter_options(vehicle_queryset):
    """Derives distinct filter choices directly from vehicle database entries."""
    makes = (
        vehicle_queryset.exclude(make__isnull=True)
        .exclude(make__exact='')
        .values_list('make', flat=True)
        .distinct()
        .order_by('make')
    )
    body_types = (
        vehicle_queryset.exclude(body_type__isnull=True)
        .exclude(body_type__exact='')
        .values_list('body_type', flat=True)
        .distinct()
        .order_by('body_type')
    )
    locations = (
        vehicle_queryset.exclude(location__isnull=True)
        .exclude(location__exact='')
        .values_list('location', flat=True)
        .distinct()
        .order_by('location')
    )
    return makes, body_types, locations


@login_required
def vehicle_tender_list_view(request):
    """Active Tenders Page: Automatically displays all institutions whose deadline hasn't passed."""
    if not has_approved_subscription(request.user):
        messages.warning(
            request, 'Access restricted! Active subscription approval required.'
        )
        return redirect('user_dashboard')

    now = timezone.now()
    
    # Automatically include all institutions with a future deadline OR no set deadline
    institutions = Institution.objects.filter(
        Q(deadline__isnull=True) | Q(deadline__gt=now)
    )

    keyword = request.GET.get('q', '').strip() or request.GET.get('keyword', '').strip()
    if keyword:
        institutions = institutions.filter(
            Q(name__icontains=keyword) 
            | Q(description__icontains=keyword) 
            | Q(vehicletender__title__icontains=keyword)
        ).distinct()

    fav_inst_ids = FavoriteInstitution.objects.filter(
        user=request.user
    ).values_list('institution_id', flat=True)

    return render(
        request,
        'tenders/tender_list.html',
        {
            'institutions': institutions,
            'fav_inst_ids': set(fav_inst_ids),
        },
    )

@login_required
def winners_archive_institutions_view(request):
    """Winners Archive Page: Shows institutions whose deadline passed OR are manually marked as announced."""
    if not has_approved_subscription(request.user):
        messages.warning(
            request, 'Access restricted! Active subscription approval required.'
        )
        return redirect('user_dashboard')

    now = timezone.now()
    
    # Include institutions if their deadline passed OR if manually marked as announced
    institutions = Institution.objects.filter(
        Q(deadline__isnull=False, deadline__lte=now) | Q(is_announced=True)
    ).distinct()

    keyword = request.GET.get('q', '').strip() or request.GET.get('keyword', '').strip()
    if keyword:
        institutions = institutions.filter(
            Q(name__icontains=keyword) | Q(description__icontains=keyword)
        ).distinct()

    fav_inst_ids = FavoriteInstitution.objects.filter(
        user=request.user
    ).values_list('institution_id', flat=True)

    return render(
        request,
        'tenders/winners_archive_institutions.html',
        {
            'institutions': institutions,
            'fav_inst_ids': set(fav_inst_ids),
        },
    )
@login_required
def watchlist_view(request):
    """Watchlist Page: Displays saved institutions and vehicle tenders with full filtering."""
    if not has_approved_subscription(request.user):
        messages.warning(
            request, 'Access restricted! Active subscription approval required.'
        )
        return redirect('user_dashboard')

    now = timezone.now()
    fav_institutions = Institution.objects.filter(
        favorited_by__user=request.user
    )
    fav_vehicles = VehicleTender.objects.filter(
        favorited_by__user=request.user
    ).select_related('institution')

    keyword = request.GET.get('q', '').strip() or request.GET.get('keyword', '').strip()
    make = request.GET.get('make', '').strip()
    body_type = request.GET.get('body_type', '').strip()
    location = request.GET.get('location', '').strip()

    if keyword:
        fav_institutions = fav_institutions.filter(
            Q(name__icontains=keyword)
            | Q(vehicletender__title__icontains=keyword)
        ).distinct()
        fav_vehicles = fav_vehicles.filter(
            Q(title__icontains=keyword)
            | Q(institution__name__icontains=keyword)
        )

    if make:
        fav_institutions = fav_institutions.filter(
            vehicletender__make__iexact=make
        ).distinct()
        fav_vehicles = fav_vehicles.filter(make__iexact=make)

    if body_type:
        fav_institutions = fav_institutions.filter(
            vehicletender__body_type__iexact=body_type
        ).distinct()
        fav_vehicles = fav_vehicles.filter(body_type__iexact=body_type)

    if location:
        fav_institutions = fav_institutions.filter(
            vehicletender__location__iexact=location
        ).distinct()
        fav_vehicles = fav_vehicles.filter(location__iexact=location)

    user_saved_vehicles = VehicleTender.objects.filter(
        favorited_by__user=request.user
    )
    makes, body_types, locations = get_dynamic_filter_options(
        user_saved_vehicles
    )

    return render(
        request,
        'tenders/watchlist.html',
        {
            'fav_institutions': fav_institutions,
            'fav_vehicles': fav_vehicles,
            'makes': makes,
            'body_types': body_types,
            'locations': locations,
            'now': now,
        },
    )

@login_required
def toggle_favorite_view(request, target_type, pk):
    """Form-based POST action to toggle institutions or vehicle tenders in user watchlists."""
    if not has_approved_subscription(request.user):
        messages.warning(
            request, 'Access restricted! Active subscription approval required.'
        )
        return redirect('user_dashboard')

    if request.method == 'POST':
        if target_type == 'institution':
            inst = get_object_or_404(Institution, pk=pk)
            fav, created = FavoriteInstitution.objects.get_or_create(
                user=request.user, institution=inst
            )
            if not created:
                fav.delete()
                messages.info(
                    request, f'Removed "{inst.name}" from your watchlist.'
                )
            else:
                messages.success(request, f'Added "{inst.name}" to your watchlist!')

        elif target_type == 'vehicle':
            veh = get_object_or_404(VehicleTender, pk=pk)
            fav, created = FavoriteVehicleTender.objects.get_or_create(
                user=request.user, vehicle=veh
            )
            if not created:
                fav.delete()
                messages.info(
                    request, f'Removed "{veh.title}" from your watchlist.'
                )
            else:
                messages.success(request, f'Added "{veh.title}" to your watchlist!')

    return redirect(request.META.get('HTTP_REFERER', 'tender_list'))


@login_required
def institution_tenders_view(request, institution_pk):
    """Active Vehicle Tenders view for a single institution with vehicle-specific filtering."""
    if not has_approved_subscription(request.user):
        messages.warning(
            request, 'Access restricted! Active subscription approval required.'
        )
        return redirect('user_dashboard')

    institution = get_object_or_404(Institution, pk=institution_pk)

    now = timezone.now()
    if institution.deadline and institution.deadline <= now:
        messages.info(
            request,
            "This tender's deadline has passed. View it in the Winners Archive.",
        )
        return redirect(
            'winners_archive_tenders', institution_pk=institution.pk
        )

    base_tenders = VehicleTender.objects.filter(institution=institution)
    makes, body_types, locations = get_dynamic_filter_options(base_tenders)

    tenders = base_tenders
    make = request.GET.get('make', '').strip()
    body_type = request.GET.get('body_type', '').strip()
    location = request.GET.get('location', '').strip()

    if make:
        tenders = tenders.filter(make__iexact=make)
    if body_type:
        tenders = tenders.filter(body_type__iexact=body_type)
    if location:
        tenders = tenders.filter(location__iexact=location)

    fav_vehicle_ids = FavoriteVehicleTender.objects.filter(
        user=request.user
    ).values_list('vehicle_id', flat=True)

    return render(
        request,
        'tenders/institution_tenders.html',
        {
            'institution': institution,
            'tenders': tenders,
            'makes': makes,
            'body_types': body_types,
            'locations': locations,
            'fav_vehicle_ids': set(fav_vehicle_ids),
        },
    )


@login_required
def winners_archive_tenders_view(request, institution_pk):
    """Archived Vehicle Tender Results for a single institution with vehicle-specific filtering."""
    if not has_approved_subscription(request.user):
        messages.warning(
            request, 'Access restricted! Active subscription approval required.'
        )
        return redirect('user_dashboard')

    institution = get_object_or_404(Institution, pk=institution_pk)
    base_tenders = VehicleTender.objects.filter(institution=institution)
    makes, body_types, locations = get_dynamic_filter_options(base_tenders)

    tenders = base_tenders
    make = request.GET.get('make', '').strip()
    body_type = request.GET.get('body_type', '').strip()
    location = request.GET.get('location', '').strip()

    if make:
        tenders = tenders.filter(make__iexact=make)
    if body_type:
        tenders = tenders.filter(body_type__iexact=body_type)
    if location:
        tenders = tenders.filter(location__iexact=location)

    fav_vehicle_ids = FavoriteVehicleTender.objects.filter(
        user=request.user
    ).values_list('vehicle_id', flat=True)

    return render(
        request,
        'tenders/winners_archive_tenders.html',
        {
            'institution': institution,
            'tenders': tenders,
            'makes': makes,
            'body_types': body_types,
            'locations': locations,
            'fav_vehicle_ids': set(fav_vehicle_ids),
        },
    )