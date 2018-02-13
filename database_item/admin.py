# -*- coding: utf-8 -*-

from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import *
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

# класс выводит изображения изделия внизу карточки товара
class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 0

class ItemCategoryAdmin (admin.ModelAdmin):

    list_display = [field.name for field in ItemCategory._meta.fields]

    class Meta:
        model = ItemCategory

admin.site.register(ItemCategory, ItemCategoryAdmin)

class ItemManufacturerAdmin (admin.ModelAdmin):

    list_display = [field.name for field in ItemManufacturer._meta.fields]

    class Meta:
        model = ItemManufacturer

admin.site.register(ItemManufacturer, ItemManufacturerAdmin)

class ItemAdminResource(resources.ModelResource):
    category = fields.Field(column_name='category', attribute='category', widget=ForeignKeyWidget(ItemCategory, 'name'))
    manufacturer = fields.Field(column_name='manufacturer', attribute='manufacturer', widget=ForeignKeyWidget(ItemManufacturer, 'name'))

    class Meta:
        model = Item

class ItemAdmin (ImportExportModelAdmin): #Для импорта-экспорта используется скаченная библиотека django-import-export

    # list_display = [field.name for field in Item._meta.fields]
    list_display = ('id', 'category', 'vendor_code', 'name', 'manufacturer', 'series', 'voltage', 'power', 'is_active',
                    'price', 'currency', 'created', 'updated')
    list_display_links = ('id', 'name', 'vendor_code')
    list_editable = ('is_active', 'price', 'currency')
    list_filter = ['category', 'manufacturer', 'power']
    search_fields = ['vendor_code', 'power']

    resource_class = ItemAdminResource

admin.site.register(Item, ItemAdmin)

class ItemImageAdmin (admin.ModelAdmin):

    list_display = [field.name for field in ItemImage._meta.fields]


    class Meta:
        model = ItemImage

admin.site.register(ItemImage, ItemImageAdmin)
