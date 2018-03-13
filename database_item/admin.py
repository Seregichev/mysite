# -*- coding: utf-8 -*-

from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from django.contrib import admin
from .models import *
from import_export import resources, fields, widgets
from django_mptt_admin.admin import DjangoMpttAdmin
import json


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


# класс выводит дополнительные изделия внизу карточки товара
class AddItemInline(admin.TabularInline):
    model = AddItem
    fk_name = 'main_item'
    can_delete = False
    extra = 0

    # фильтруем выпадающий список поля доп. изделия по серии редактируемого изделия
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "adding_item":
            gotten_id = ''
            # из адреса request выбираем только id изделия
            for e in request.path_info.split('/'):
                if e.isdigit():
                    gotten_id = e
            # по полученному id изделия находим его серию и отфильтровываем выпадающий список изделий по серии

            kwargs["queryset"] = Item.objects.filter(
                series=Item.objects.filter(id=gotten_id or None, is_active=True)
                .values('series'), is_active=True)
        return super(AddItemInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


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
        # exclude = ('price') #Не обходимо удалять добавку валюты из колонки price в ручную


class ItemAdmin (ImportExportModelAdmin): #Для импорта-экспорта используется скаченная библиотека django-import-export

    list_display = ('id', 'category', 'vendor_code', 'name', 'compatibility_code', 'manufacturer', 'series', 'voltage',
                    'power', 'is_active', 'price')
    list_display_links = ('id', 'name', 'vendor_code')
    list_editable = ('is_active', 'price')
    list_filter = ['category', 'manufacturer', 'series', 'power', 'voltage', 'compatibility_code',]
    search_fields = ['vendor_code', 'category', 'name', 'voltage', 'series', 'power', 'compatibility_code',]

    inlines = [AddItemInline, ItemImageInline]

    resource_class = ItemAdminResource
    empty_value_display = '-empty-'

    fieldsets = (
        (None, {
            'fields': ('category', 'manufacturer', 'series', 'vendor_code', 'compatibility_code', 'name', 'description',
                       'price', 'is_active')
        }),
        (u'Технические характеристики', {
            'classes': ('collapse',),
            'fields': ('voltage', ('current', 'type_current'), 'power', 'height', 'width', 'depth', 'area', 'variables'),
        }),
    )


admin.site.register(Item, ItemAdmin)


class ItemImageAdmin (admin.ModelAdmin):

    list_display = [field.name for field in ItemImage._meta.fields]


    class Meta:
        model = ItemImage


admin.site.register(ItemImage, ItemImageAdmin)


class AddItemAdmin (ImportExportModelAdmin):

    list_display = [field.name for field in AddItem._meta.fields]

    class Meta:
        model = AddItem


admin.site.register(AddItem, AddItemAdmin)