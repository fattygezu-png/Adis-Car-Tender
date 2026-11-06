from django.contrib import admin
from .models import (
    FavoriteInstitution,
    FavoriteVehicleTender,
    Institution,
    VehicleTender,
)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'deadline',
        'is_announced',
        'is_dismissed',
    )
    list_editable = ('is_announced', 'is_dismissed')
    search_fields = ('name',)

    def save_model(self, request, obj, form, change):
        obj.save()


@admin.register(VehicleTender)
class VehicleTenderAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'institution',
        'starting_price',
        'is_announced',
        'is_dismissed',
        'winner_name',
    )
    list_editable = ('is_announced', 'is_dismissed')
    list_filter = ('institution', 'is_announced', 'is_dismissed')
    search_fields = ('title', 'make', 'winner_name')

    def save_model(self, request, obj, form, change):
        obj.save()


admin.site.register(FavoriteInstitution)
admin.site.register(FavoriteVehicleTender)