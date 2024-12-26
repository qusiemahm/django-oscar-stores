from modeltranslation.translator import translator, TranslationOptions
from .models import Store

class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'city', 'state')  # Specify the fields to translate

translator.register(Store, ProductTranslationOptions)