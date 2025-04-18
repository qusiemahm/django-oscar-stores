from django.contrib.gis.db.models import Manager, PointField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from oscar.apps.address.abstract_models import AbstractAddress
from oscar.core.utils import slugify
from django.core.cache import cache
from django.utils.timezone import make_aware, now
from django.contrib.gis.geos import Point
from decimal import Decimal as D

from server.apps.user.models import City
from server.apps.vendor.models import Vendor
from stores.managers import StoreManager
from stores.utils import get_geodetic_srid
from django.utils import timezone
from datetime import datetime, time, timedelta


# Re-use Oscar's address model
class StoreAddress(AbstractAddress):
    store = models.OneToOneField(
        'stores.Store',
        models.CASCADE,
        verbose_name=_("Store"),
        related_name="address"
    )
    # line4 = None
    class Meta:
        abstract = True
        app_label = 'stores'

    @property
    def street(self):
        """
        Summary of the 3 line fields
        """
        return "\n".join(filter(bool, [self.line1, self.line2, self.line3]))


class StoreGroup(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True)

    class Meta:
        abstract = True
        app_label = 'stores'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Store(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100, null=True)

    # Contact details
    manager_name = models.CharField(
        _('Manager name'), max_length=200, blank=True, null=True)
    phone = models.CharField(_('Phone'), max_length=64, blank=True, null=True)
    email = models.CharField(_('Email'), max_length=100, blank=True, null=True)

    reference = models.CharField(
        _("Reference"),
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        help_text=_("A reference number that uniquely identifies this store"))

    image = models.ImageField(
        _("Image"),
        upload_to="uploads/store-images",
        blank=True, null=True)
    description = models.CharField(
        _("Description"),
        max_length=2000,
        blank=True, null=True)
    location = PointField(
        _("Location"),
        srid=get_geodetic_srid(),
        default=Point(46.6753, 24.7136)
    )
    is_main = models.BooleanField(default=False)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=100, null=True, blank=True)


    group = models.ForeignKey(
        'stores.StoreGroup',
        models.PROTECT,
        related_name='stores',
        verbose_name=_("Group"),
        null=True,
        blank=True
    )
    minimum_order_value = models.DecimalField(
        _("Minimum Order Value"),
        max_digits=12,
        decimal_places=2,
        default=15,
        help_text=_("Minimum order value required for this store")
    )
    is_drive_thru = models.BooleanField(_("Is Drive Trru"), default=False)
    is_active = models.BooleanField(_("Is active"), default=True)
    
    preparing_time = models.PositiveIntegerField(
        _("Preparing Time (minutes)"),
        default=30,  # Default preparation time
        help_text=_("Estimated time (in minutes) required for order preparation")
    )
    rating = models.FloatField(
        _("Rating"),
        default=0,
        help_text=_("Average rating of the store")
    )
    total_ratings = models.PositiveIntegerField(
        _("Total Ratings"),
        default=0,
        help_text=_("Total number of ratings received")
    )
    objects = StoreManager()

    class Meta:
        abstract = True
        ordering = ('name',)
        app_label = 'stores'
        
    def validate_minimum_order(self, basket_total):
        """
        Validate if basket meets minimum order requirement
        
        Args:
            basket_total (Decimal or str): Total amount of the basket
            
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        # Convert basket_total to Decimal if it's not already
        basket_total = D(str(basket_total))
        minimum_value = D(str(self.minimum_order_value))
        
        if basket_total < minimum_value:
            return False, _("Minimum order value for this store is %(amount)s") % {
                'amount': minimum_value
            }
        return True, None

    def save(self, *args, **kwargs):
        if self.pk is None:  # Check only for new branches
            # Fetch the vendor's business details
            business_details = getattr(self.vendor, 'business_details', None)
            if business_details:
                max_branches = business_details.branches_count
                current_branches = self.vendor.branches.count()
                if current_branches >= max_branches:
                    raise ValidationError(
                        _('The maximum number of branches (%d) for this vendor has been reached.') % max_branches
                    )
        if not self.slug:
            self.slug = slugify(self.name)
        if self.pk:
            cache_key = f'store_status_{self.pk}'
            cache.delete(cache_key)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('stores:detail', kwargs={'dummyslug': self.slug,
                                                'pk': self.pk})

    @property
    def has_contact_details(self):
        return any([self.manager_name, self.phone, self.email])

    @property
    def is_open(self):
        """
        Determines if the store is currently open based on the current status.
        Utilizes the shared _get_current_status method for consistency.
        """
        status, _ = self._get_current_status()
        return status == 'Open'

    @property
    def status_info(self):
        """
        Provides detailed status information of the store.
        Utilizes the shared _get_current_status method for consistency.
        """
        status, remaining_time = self._get_current_status()
        return {
            'status': status,
            'remaining_time': remaining_time
        }

    def _get_current_status(self):
        """
        Determines the current status of the store.
        Returns:
            Tuple[str, timedelta or None]: Status and remaining time (if applicable).
        Prioritizes opening hours: returns 'Closed' if outside working hours.
        """
        cache_key = f'store_status_{self.pk}'
        cached_status = cache.get(cache_key)
        if cached_status is not None:
            return cached_status

        now = timezone.now()
        current_time = now.time()
        current_weekday = now.isoweekday()

        # Step 1: Check OpeningPeriod
        opening_periods = self.opening_periods.filter(weekday=current_weekday)
        within_opening_hours = False
        for period in opening_periods:
            start_time = period.start or time(0, 0)
            end_time = period.end or time(23, 59, 59)
            if start_time <= current_time <= end_time:
                within_opening_hours = True
                break

        if not within_opening_hours:
            # Not within opening hours, mark as Closed without checking StoreStatus
            status = 'Closed'
            cache.set(cache_key, (status, None), timeout=60)
            return status, None

        # Step 2: Within opening hours, check the latest StoreStatus
        active_status = self.statuses.filter(
            set_at__lte=now,
            expires_at__gte=now
        ).order_by('-set_at').first()

        if active_status:
            status_display = active_status.get_status_display()
            if active_status.status in [StoreStatus.StatusChoices.BUSY, StoreStatus.StatusChoices.CLOSED]:
                remaining_time = active_status.expires_at - now
                remaining_time = max(remaining_time, timedelta(seconds=0))
                cache.set(cache_key, (status_display, remaining_time), timeout=60)
                return status_display, remaining_time
            elif active_status.status == StoreStatus.StatusChoices.OPEN:
                status = 'Open'
            else:
                status = 'Closed'  # Fallback
        else:
            # No active status, default to open since within time range
            status = 'Open'

        cache.set(cache_key, (status, None), timeout=60)
        return status, None
    
class OpeningPeriod(models.Model):
    PERIOD_FORMAT = _("%(start)s - %(end)s")
    (MONDAY, TUESDAY, WEDNESDAY, THURSDAY,
     FRIDAY, SATURDAY, SUNDAY) = range(1, 8)
    WEEK_DAYS = {
        MONDAY: _("Monday"),
        TUESDAY: _("Tuesday"),
        WEDNESDAY: _("Wednesday"),
        THURSDAY: _("Thursday"),
        FRIDAY: _("Friday"),
        SATURDAY: _("Saturday"),
        SUNDAY: _("Sunday"),
    }
    store = models.ForeignKey('stores.Store', models.CASCADE, verbose_name=_("Store"),
                              related_name='opening_periods')

    weekday_choices = [(k, v) for k, v in WEEK_DAYS.items()]
    weekday = models.PositiveIntegerField(
        _("Weekday"),
        choices=weekday_choices)
    start = models.TimeField(
        _("Start"),
        null=True,
        blank=True,
        help_text=_("Leaving start and end time empty is displayed as 'Closed'"))
    end = models.TimeField(
        _("End"),
        null=True,
        blank=True,
        help_text=_("Leaving start and end time empty is displayed as 'Closed'"))

    def __str__(self):
        return "%s: %s to %s" % (self.weekday, self.start, self.end)

    class Meta:
        abstract = True
        ordering = ['weekday']
        verbose_name = _("Opening period")
        verbose_name_plural = _("Opening periods")
        app_label = 'stores'

    def clean(self):
        if self.start and self.end and self.end <= self.start:
            raise ValidationError(_("Start must be before end"))


# class StoreStock(models.Model):
#     store = models.ForeignKey(
#         'stores.Store',
#         models.CASCADE,
#         verbose_name=_("Store"),
#         related_name='stock'
#     )
#     product = models.ForeignKey(
#         'catalogue.Product',
#         models.CASCADE,
#         verbose_name=_("Product"),
#         related_name="store_stock"
#     )

#     # Stock level information
#     num_in_stock = models.PositiveIntegerField(
#         _("Number in stock"),
#         default=0,
#         blank=True,
#         null=True)

#     # The amount of stock allocated in store but not fed back to the master
#     num_allocated = models.IntegerField(
#         _("Number allocated"),
#         default=0,
#         blank=True,
#         null=True)

#     location = models.CharField(
#         _("In store location"),
#         max_length=50,
#         blank=True,
#         null=True)

#     # Date information
#     date_created = models.DateTimeField(
#         _("Date created"),
#         auto_now_add=True)
#     date_updated = models.DateTimeField(
#         _("Date updated"),
#         auto_now=True,
#         db_index=True)

#     class Meta:
#         abstract = True
#         verbose_name = _("Store stock record")
#         verbose_name_plural = _("Store stock records")
#         unique_together = ("store", "product")
#         app_label = 'stores'

#     objects = Manager()

#     def __str__(self):
#         if self.store and self.product:
#             return "%s @ %s" % (self.product.title, self.store.name)
#         return "Store Stock"

#     @property
#     def is_available_to_buy(self):
#         return self.num_in_stock > self.num_allocated

class StoreStatus(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = 'open', _('Open')
        CLOSED = 'closed', _('Closed')
        BUSY = 'busy', _('Busy')

    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(max_length=10, choices=StatusChoices.choices)
    duration = models.DurationField(null=True, blank=True, help_text=_("Duration for which the status is active"))
    set_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)  # Assign set_at if new

        # Calculate expires_at based on duration
        if self.duration:
            new_expires_at = self.set_at + self.duration
        else:
            # Permanent status: expires at end of the day
            today = self.set_at.date()
            new_expires_at = datetime.combine(today, time(23, 59, 59))
            new_expires_at = make_aware(new_expires_at)

        # Update expires_at without triggering save() again
        StoreStatus.objects.filter(pk=self.pk).update(expires_at=new_expires_at)

    def __str__(self):
        return f"{self.store.name} - {self.get_status_display()}"

    class Meta:
        verbose_name = _("Store Status")
        verbose_name_plural = _("Store Statuses")
        ordering = ['-set_at']
        

class StoreRating(models.Model):
    store = models.ForeignKey(
        'stores.Store',
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_("Store")
    )
    order = models.OneToOneField(
        'order.Order',
        on_delete=models.CASCADE,
        related_name='store_rating',
        verbose_name=_("Order"),
        help_text=_("The order associated with this rating")
    )
    customer = models.ForeignKey(
        'user.Customer',
        on_delete=models.CASCADE,
        related_name='store_ratings',
        verbose_name=_("Customer")
    )
    rating = models.PositiveSmallIntegerField(
        _("Rating"),
        choices=[(i, str(i)) for i in range(1, 6)],  # 1-5 rating scale
        help_text=_("Rate from 1 to 5 stars")
    )
    comment = models.TextField(
        _("Comment"),
        blank=True,
        null=True,
        help_text=_("Optional feedback about your experience")
    )
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True
    )

    class Meta:
        abstract = True
        verbose_name = _("Store Rating")
        verbose_name_plural = _("Store Ratings")
        unique_together = ('store', 'order')  # Ensure one rating per order
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'rating']),
            models.Index(fields=['customer', 'created_at'])
        ]

    def __str__(self):
        return f"Order #{self.order.number} - {self.store.name} ({self.rating} stars)"

    def clean(self):
        """Validate that the order belongs to the store and customer"""
        if self.order.user != self.customer.user:
            raise ValidationError(_("You can only rate orders that belong to you."))
        
        if self.store != self.order.store:
            raise ValidationError(_("Rating must be for the store that fulfilled the order."))
        
        # if self.order.status != 'Completed':
        #     raise ValidationError(_("You can only rate completed orders."))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update store's average rating and total ratings
        store_ratings = self.store.ratings.aggregate(
            avg_rating=models.Avg('rating'),
            total_ratings=models.Count('id')
        )
        
        # Update the store model
        self.store.rating = store_ratings['avg_rating'] or 0
        self.store.total_ratings = store_ratings['total_ratings'] or 0
        self.store.save()
        
