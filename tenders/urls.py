from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicle_tender_list_view, name='tender_list'),
    path(
        'institution/<int:institution_pk>/',
        views.institution_tenders_view,
        name='institution_tenders',
    ),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path(
        'toggle-favorite/<str:target_type>/<int:pk>/',
        views.toggle_favorite_view,
        name='toggle_favorite',
    ),
    path(
        'winners/',
        views.winners_archive_institutions_view,
        name='winners_archive',
    ),
    path(
        'winners/<int:institution_pk>/',
        views.winners_archive_tenders_view,
        name='winners_archive_tenders',
    ),
]