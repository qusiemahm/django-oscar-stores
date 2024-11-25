from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import generic
from extra_views import CreateWithInlinesView, InlineFormSetFactory, UpdateWithInlinesView
from oscar.core.loading import get_class, get_classes, get_model
from django.http import Http404

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


class StoreListView(generic.ListView):
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
        qs = self.model.objects.all()
        # Restrict to stores for the current vendor
        if self.request.user.is_authenticated and hasattr(self.request.user, 'vendor_users'):

            vendor = self.request.user.vendor_users.first()
            qs = qs.filter(vendor=vendor)
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
            form.instance.vendor = self.request.user.vendor_users.first()
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
            vendor = self.request.user.vendor_users.first()
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
        print("self.request.user.vendor_users: ", self.request.user.vendor_users.first())

        if obj.vendor != self.request.user.vendor_users.first():
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
        if obj.vendor != self.request.user.vendor_users.first():
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
