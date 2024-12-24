from oscar.core.loading import is_model_registered
from auditlog.registry import auditlog
from django.utils.translation import gettext_lazy as _

from . import abstract_models

__all__ = []


if not is_model_registered('stores', 'StoreAddress'):
    class StoreAddress(abstract_models.StoreAddress):
        pass

    __all__.append('StoreAddress')


if not is_model_registered('stores', 'StoreGroup'):
    class StoreGroup(abstract_models.StoreGroup):
        pass

    __all__.append('StoreGroup')


if not is_model_registered('stores', 'Store'):
    class Store(abstract_models.Store):
        pass

        class Meta:
            verbose_name = _("Branch")
            verbose_name_plural = _("Branches")
            app_label = 'stores'

    __all__.append('Store')


if not is_model_registered('stores', 'OpeningPeriod'):
    class OpeningPeriod(abstract_models.OpeningPeriod):
        pass

    __all__.append('OpeningPeriod')


if not is_model_registered('stores', 'StoreStock'):
    class StoreStock(abstract_models.StoreStock):
        pass

    __all__.append('StoreStock')


auditlog.register(StoreAddress)
auditlog.register(StoreGroup)
auditlog.register(Store)
auditlog.register(OpeningPeriod)
auditlog.register(StoreStock)
