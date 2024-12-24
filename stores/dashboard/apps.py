from django.urls import path
from oscar.core.application import OscarDashboardConfig
from oscar.core.loading import get_class


class StoresDashboardConfig(OscarDashboardConfig):

    name = 'stores.dashboard'
    label = 'stores_dashboard'

    namespace = 'stores-dashboard'

    # default_permissions = ['is_staff']

    def has_permission(self, user):
        """
        Override this method to check if the user is associated with an active vendor.
        """
        # Import the function only when needed to avoid circular dependency issues
        from server.apps.vendor.utils import is_user_active_vendor
        return user.is_authenticated and is_user_active_vendor(user)

    def ready(self):
        self.store_list_view = get_class('stores.dashboard.views', 'StoreListView')
        self.store_create_view = get_class('stores.dashboard.views', 'StoreCreateView')
        self.store_update_view = get_class('stores.dashboard.views', 'StoreUpdateView')
        self.store_delete_view = get_class('stores.dashboard.views', 'StoreDeleteView')

        self.store_group_list_view = get_class('stores.dashboard.views', 'StoreGroupListView')
        self.store_group_create_view = get_class('stores.dashboard.views', 'StoreGroupCreateView')
        self.store_group_update_view = get_class('stores.dashboard.views', 'StoreGroupUpdateView')
        self.store_group_delete_view = get_class('stores.dashboard.views', 'StoreGroupDeleteView')
        self.change_store_status = get_class('stores.dashboard.views', 'change_store_status')

    def get_urls(self):
        urls = [
            path('', self.store_list_view.as_view(), name='store-list'),
            path('create/', self.store_create_view.as_view(), name='store-create'),
            path('update/<int:pk>/', self.store_update_view.as_view(), name='store-update'),
            path('delete/<int:pk>/', self.store_delete_view.as_view(), name='store-delete'),
            path('groups/', self.store_group_list_view.as_view(), name='store-group-list'),
            path('groups/create/', self.store_group_create_view.as_view(), name='store-group-create'),
            path('groups/update/<int:pk>/', self.store_group_update_view.as_view(), name='store-group-update'),
            path('groups/delete/<int:pk>/', self.store_group_delete_view.as_view(), name='store-group-delete'),
            path('change-store-status/', self.change_store_status, name='change_store_status'),

        ]
        return self.post_process_urls(urls)
