from django.contrib import admin
from oscar.core.loading import get_model
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django import forms
from mapwidgets.widgets import GoogleMapPointFieldWidget

Store = get_model('stores', 'Store')
# StoreGroup = get_model('stores', 'StoreGroup')
OpeningPeriod = get_model('stores', 'OpeningPeriod')
# StoreStock = get_model('stores', 'StoreStock')
StoreAddress = get_model('stores', 'StoreAddress')
StoreStatus = get_model('stores', 'StoreStatus')
from django.http import HttpResponse
import csv

def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stores.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Vendor', 'City', 'Active'])
    for store in queryset:
        writer.writerow([store.name, store.vendor.name, store.city, store.is_active])
    return response
export_as_csv.short_description = "Export Selected to CSV"

class OpeningPeriodInline(admin.TabularInline):  # Or admin.StackedInline
    model = OpeningPeriod
    extra = 1  # Number of empty forms displayed


class StoreStatusInline(admin.TabularInline):
    model = StoreStatus
    extra = 1

def deactivate_stores(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_stores.short_description = "Deactivate selected stores"


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'
        widgets = {
            'location': GoogleMapPointFieldWidget,  # Correct widget class name
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark specific fields as required
        self.fields['name_en'].required = True
        self.fields['name_ar'].required = True
        self.fields['description_en'].required = True
        self.fields['description_ar'].required = True

class StoreAdmin(admin.ModelAdmin):
    lang = get_language()
    list_display = ('name', 'vendor', 'city', 'is_active')  # vendor__name corrected to vendor
    form = StoreForm
    view_on_site = False
    actions = [deactivate_stores, export_as_csv]
    # Add search fields
    search_fields = ('name', 'vendor__name', 'city', 'state', 'description')
    inlines = [OpeningPeriodInline, StoreStatusInline]
    # Add filters
    list_filter = ('is_active', 'city', 'state', 'vendor',)
    readonly_fields = ('rating', 'total_ratings')
    fieldsets = (
    ('Basic Information', {
        'fields': ('name_en', 'name_ar', 'slug', 'description_ar', 'description_en', 'vendor', 'preparing_time','minimum_order_value','rating','total_ratings', 'image')
    }),
    ('Location Information', {
        'fields': ('city', 'location'),
        'classes': ('collapse',),
    }),
    ('Status', {
        'fields': ('is_active',),
    }),
)


class StoreStatusAdmin(admin.ModelAdmin):
    list_display = ('store', 'status', 'set_at', 'expires_at')
    list_filter = ('status',)
    search_fields = ('store__name',)

admin.site.site_header = _("JAY")
admin.site.site_title = _("JAY Admin")
admin.site.index_title = _("JAY Admin")
admin.site.register(Store, StoreAdmin)
# admin.site.register(StoreGroup)
admin.site.register(OpeningPeriod)
# admin.site.register(StoreStock)
admin.site.register(StoreAddress)
admin.site.register(StoreStatus, StoreStatusAdmin)
