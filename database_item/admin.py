# -*- coding: utf-8 -*-

from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from django.contrib import admin
from .models import *
from import_export import resources, fields, widgets
from django_mptt_admin.admin import DjangoMpttAdmin
import json
from django_admin_hstore_widget.forms import HStoreFormField

class JSONWidget(widgets.Widget):
    """ Convert data into JSON for serialization.
    """
    def clean(self, value, row=None, *args, **kwargs):
        return json.loads(value)

    def render(self, value, obj=None):
        if value is None:
            return ""
        return json.dumps(value)

class JSONResourceMixin(object):
    """ Override ModelResource to provide JSON field support.
    """

    @classmethod
    def widget_from_django_field(cls, f, default=widgets.Widget):

        if f.get_internal_type() in ('DictionaryField',):
            return JSONWidget
        else:
            return super().widget_from_django_field(f)


# класс выводит изображения изделия внизу карточки товара
class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 0

class CategoryResource(resources.ModelResource):

    class Meta:
        model = ItemCategory
        fields = ('id', 'name',)
        exclude = ('parent',)

class ItemCategoryAdmin (ImportExportModelAdmin, DjangoMpttAdmin):
    mptt_level_indent = 20
    resource_class = CategoryResource
    empty_value_display = '-empty-'

admin.site.register(ItemCategory, ItemCategoryAdmin)

class ItemManufacturerAdmin (ImportExportActionModelAdmin):

    list_display = [field.name for field in ItemManufacturer._meta.fields]

    class Meta:
        model = ItemManufacturer

admin.site.register(ItemManufacturer, ItemManufacturerAdmin)

class ItemAdminResource(JSONResourceMixin, resources.ModelResource):
    category = fields.Field(column_name='category', attribute='category', widget=widgets.ForeignKeyWidget(ItemCategory, 'name'))
    manufacturer = fields.Field(column_name='manufacturer', attribute='manufacturer', widget=widgets.ForeignKeyWidget(ItemManufacturer, 'name'))

    class Meta:
        model = Item


class ItemAdmin (ImportExportModelAdmin): #Для импорта-экспорта используется скаченная библиотека django-import-export

    list_display = ('id', 'category', 'vendor_code', 'name', 'manufacturer', 'series', 'voltage', 'power', 'is_active',
                    'price')
    list_display_links = ('id', 'name', 'vendor_code')
    list_editable = ('is_active', 'price')
    list_filter = ['category', 'manufacturer', 'power']
    search_fields = ['vendor_code', 'power']

    inlines = [ItemImageInline]

    resource_class = ItemAdminResource
    empty_value_display = '-empty-'



admin.site.register(Item, ItemAdmin)

class ItemImageAdmin (admin.ModelAdmin):

    list_display = [field.name for field in ItemImage._meta.fields]


    class Meta:
        model = ItemImage

admin.site.register(ItemImage, ItemImageAdmin)
