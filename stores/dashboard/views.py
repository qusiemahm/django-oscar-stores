from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import generic
from extra_views import CreateWithInlinesView, InlineFormSetFactory, UpdateWithInlinesView
from oscar.core.loading import get_class, get_classes, get_model
from django.http import Http404
from django.utils.timezone import now, timedelta
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.core.cache import cache
from server.apps.vendor.mixins import VendorMixin

MapsContextMixin = get_class('stores.views', 'MapsContextMixin')
(DashboardStoreSearchForm,
 OpeningHoursInline,
 OpeningPeriodForm,
 StoreAddressForm,
 StoreForm) = get_classes('stores.dashboard.forms', ('DashboardStoreSearchForm',
                                                     'OpeningHoursInline',
                                                     'OpeningPeriodForm',
                                                     'StoreAddressForm',
                                                     'StoreForm'))
Store = get_model('stores', 'Store')
StoreGroup = get_model('stores', 'StoreGroup')
OpeningPeriod = get_model('stores', 'OpeningPeriod')
StoreAddress = get_model('stores', 'StoreAddress')
StoreStatus = get_model('stores', 'StoreStatus')


class StoreListView(VendorMixin, generic.ListView):
    model = Store
    template_name = "stores/dashboard/store_list.html"
    context_object_name = "store_list"
    paginate_by = 20
    filterform_class = DashboardStoreSearchForm

    def get_title(self):
        data = getattr(self.filterform, 'cleaned_data', {})

        name = data.get('name', None)
        address = data.get('address', None)

        if name and not address:
            return gettext('Stores matching "%s"') % (name)
        elif name and address:
            return gettext('Stores matching "%s" near "%s"') % (name, address)
        elif address:
            return gettext('Stores near "%s"') % (address)
        else:
            return gettext('Stores')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filterform'] = self.filterform
        data['queryset_description'] = self.get_title()
        return data

    def get_queryset(self):
        # Restrict to stores for the current vendor
        if self.request.user.is_authenticated:
            vendor = self.get_vendor()
            qs = self.model.objects.filter(vendor=vendor)

        else:
            qs = qs.none()  # If no vendor is associated, return an empty queryset

        self.filterform = self.filterform_class(self.request.GET)
        if self.filterform.is_valid():
            qs = self.filterform.apply_filters(qs)
        return qs


class StoreAddressInline(InlineFormSetFactory):

    model = StoreAddress
    form_class = StoreAddressForm
    factory_kwargs = {
        'extra': 1,
        'max_num': 1,
        'can_delete': False,
    }


class OpeningPeriodInline(InlineFormSetFactory):
    extra = 7
    max_num = 7
    model = OpeningPeriod
    form_class = OpeningPeriodForm


class StoreEditMixin(MapsContextMixin):
    inlines = [OpeningHoursInline, StoreAddressInline]

    def forms_valid(self, form, inlines):
        # Set the vendor for new stores created
        if not form.instance.pk:  # Only set the vendor on creation, not update
            form.instance.vendor = self.request.user.vendor
        return super().forms_valid(form, inlines)

class StoreCreateView(StoreEditMixin, CreateWithInlinesView):
    model = Store
    template_name = "stores/dashboard/store_update.html"
    form_class = StoreForm
    success_url = reverse_lazy('stores-dashboard:store-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = _("Create new store")
        return ctx

    def forms_invalid(self, form, inlines):
        messages.error(
            self.request,
            "Your submitted data was not valid - please correct the below errors")
        return super().forms_invalid(form, inlines)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        inlines = self.construct_inlines()

        if form.is_valid():
            # Save the store instance to get a primary key
            vendor = self.request.user.vendor
            if not vendor:
                messages.error(self.request, _("You do not have an associated vendor to create a store."))
                return self.form_invalid(form)
            
            form.instance.vendor = vendor
            self.object = form.save()  # Save the primary instance

            # Validate and save inlines
            if all(inline.is_valid() for inline in inlines):
                return self.forms_valid(form, inlines)
            else:
                return self.forms_invalid(form, inlines)
        else:
            return self.form_invalid(form)


class StoreUpdateView(StoreEditMixin, UpdateWithInlinesView):
    model = Store
    template_name = "stores/dashboard/store_update.html"
    form_class = StoreForm
    success_url = reverse_lazy('stores-dashboard:store-list')

    def get_object(self, queryset=None):
        """Override to ensure the store belongs to the current vendor."""
        obj = super().get_object(queryset)
        print("obj: ", obj)
        print("obj.vendor: ", obj.vendor)
        print("self.request.user.vendor: ", self.request.user.vendor)

        if obj.vendor != self.request.user.vendor:
            raise Http404("You do not have permission to access this store.")
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = self.object.name
        return ctx

    def forms_invalid(self, form, inlines):
        messages.error(
            self.request,
            "Your submitted data was not valid - please correct the below errors")
        return super().forms_invalid(form, inlines)

    def forms_valid(self, form, inlines):
        msg = render_to_string('stores/dashboard/messages/store_saved.html',
                               {'store': self.object})
        messages.success(self.request, msg, extra_tags='safe')
        return super().forms_valid(form, inlines)


class StoreDeleteView(generic.DeleteView):
    model = Store
    template_name = "stores/dashboard/store_delete.html"
    success_url = reverse_lazy('stores-dashboard:store-list')

    def get_object(self, queryset=None):
        """Override to ensure the store belongs to the current vendor."""
        obj = super().get_object(queryset)
        if obj.vendor != self.request.user.vendor:
            raise Http404("You do not have permission to delete this store.")
        return obj
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        for time in self.object.opening_periods.all():
            time.delete()
        return super().delete(request, *args, **kwargs)


class StoreGroupListView(generic.ListView):
    model = StoreGroup
    context_object_name = 'group_list'
    template_name = "stores/dashboard/store_group_list.html"


class StoreGroupCreateView(generic.CreateView):
    model = StoreGroup
    fields = ['name', 'slug']
    template_name = "stores/dashboard/store_group_update.html"
    success_url = reverse_lazy('stores-dashboard:store-group-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = _("Create new store group")
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Store group created"))
        return response


class StoreGroupUpdateView(generic.UpdateView):
    model = StoreGroup
    fields = ['name', 'slug']
    template_name = "stores/dashboard/store_group_update.html"
    success_url = reverse_lazy('stores-dashboard:store-group-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = self.object.name
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Store group updated"))
        return response


class StoreGroupDeleteView(generic.DeleteView):
    model = StoreGroup
    template_name = "stores/dashboard/store_group_delete.html"
    success_url = reverse_lazy('stores-dashboard:store-group-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Store group deleted"))
        return response

@csrf_protect
@require_POST
def change_store_status(request):
    store_id = request.POST.get('store_id')
    new_status = request.POST.get('status')
    duration_choice = request.POST.get('duration')

    # Validate required fields
    if not store_id or not new_status:
        messages.error(request, "Invalid store ID or status.")
        return redirect(reverse('stores-dashboard:store-list'))
    
    # Fetch the store or return 404 if not found
    store = get_object_or_404(Store, id=store_id)
    print("status: ", store, new_status, duration_choice)

    # Calculate duration based on duration_choice
    duration_mapping = {
        "end_of_day": timedelta(hours=now().hour, minutes=now().minute, seconds=now().second, microseconds=now().microsecond),
        "permanently": None,
        "1_hour": timedelta(hours=1),
        "2_hours": timedelta(hours=2),
    }

    duration = duration_mapping.get(duration_choice, None)

    # Determine duration to set
    if duration_choice == "end_of_day":
        # Calculate duration until the end of the day
        end_of_day = now().replace(hour=23, minute=59, second=59, microsecond=999999)
        duration = end_of_day - now()

    # Try to update an existing active StoreStatus
    try:
        # Create a new StoreStatus entry
        StoreStatus.objects.create(
            store=store,
            status=new_status,
            duration=duration,
            set_at=now(),
            expires_at=(now() + duration) if duration else None,
        )
    except StoreStatus.DoesNotExist:
        try:
            # Update or create the StoreStatus object
            StoreStatus.objects.update_or_create(
                store=store,  # Match condition
                defaults={
                    'status': new_status,  # Fields to update or set
                    'duration': duration,
                    'set_at': now()
                }
            )
            messages.success(request, f"Store status set to {new_status} successfully.")
        except IntegrityError:
            # Handle the case where another active StoreStatus was created concurrently
            messages.error(request, "Unable to set store status due to a concurrent update. Please try again.")
    
    # Invalidate the cache for the store's current status
    cache_key = f'store_status_{store.pk}'
    cache.delete(cache_key)

    # Redirect back to the store list page or any other desired page
    return redirect(reverse('stores-dashboard:store-list'))