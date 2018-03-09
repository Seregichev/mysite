# -*- coding: utf-8 -*-
from django.db import models
from django_hstore import hstore
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.encoding import python_2_unicode_compatible
from decimal import Decimal
from tinymce.models import HTMLField
from filer.fields.image import FilerImageField
from djmoney.models.fields import MoneyField

TYPE_CURRENT_CHOICES = (
    ('AC','AC'),
    ('DC','DC')
)
TYPE_PROTECT_CLASS = (
    ('10','10'),
    ('20','20'),
    ('30','30'),
    ('40','40'),
)
@python_2_unicode_compatible
class ItemCategory(MPTTModel):
    name = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Название")
    parent = TreeForeignKey('self', null=True, blank=True, default=None, related_name='children', verbose_name="Родитель", db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        verbose_name = "Категория изделия"
        verbose_name_plural = "Категории изделий"

@python_2_unicode_compatible
class ItemManufacturer(models.Model):
    short_name = models.CharField(max_length=5, blank=True, null=True, default=None, verbose_name="Сокращение")
    name = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Название")

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = "Производитель изделия"
        verbose_name_plural = "Производители изделий"

@python_2_unicode_compatible
class Item(models.Model):
    category = models.ForeignKey(ItemCategory, blank=True, null=True, default=None, verbose_name="Категория",
                                 on_delete=models.DO_NOTHING)
    manufacturer = models.ForeignKey(ItemManufacturer, blank=True, null=True, default=None,
                                     verbose_name="Производитель", on_delete=models.DO_NOTHING)
    series = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Серия")
    name = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Название")
    vendor_code = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Артикул")
    description = HTMLField(blank=True, null=True, default=None, verbose_name="Описание")

    voltage = models.DecimalField(max_digits=7, decimal_places=0, default=0, verbose_name="Напряжение [В]")
    current = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name="Ток [А]")
    type_current = models.CharField(choices=TYPE_CURRENT_CHOICES, max_length=3, blank=True, null=True, default='AC',
                                    verbose_name="Вид тока")
    power = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name="Мощность [кВт]")

    height = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Высота")
    width = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ширина")
    depth = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Глубина")
    area = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Площадь")

    variables = hstore.DictionaryField(blank=True, null=True, default=dict, db_index=True, verbose_name=u"Переменные")

    objects = hstore.HStoreManager()

    is_active = models.BooleanField(default=True, verbose_name="Активно?")
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR', verbose_name="Цена")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Создано")
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name="Обновленно")

    def __str__(self):
        return "%s, %s" % (self.vendor_code, self.name)

    class Meta:
        verbose_name = "Изделие"
        verbose_name_plural = "Изделия"

    def save(self, *args, **kwargs):
        if self.height > 0 and self.width and self.area == 0:
            self.area = self.height * self.width
        if self.type_current == 'AC':
            if self.current > 0 and self.power == 0:
                self.power = (self.voltage * self.current * Decimal('0.89')) / 1000
            if self.power > 0 and self.current == 0:
                self.current = (Decimal(self.power) * Decimal(1000) / (Decimal(self.voltage) * Decimal('0.8')))
        elif self.type_current == 'DC':
            if self.current > 0 and self.power == 0:
                self.power = (self.voltage * self.current) / 1000
            if self.power > 0 and self.current == 0:
                self.current = (Decimal(self.power) * Decimal(1000) / (Decimal(self.voltage)))
        super(Item, self).save(*args, **kwargs)

@python_2_unicode_compatible
class ItemImage(models.Model):
    item = models.ForeignKey(Item, blank=True, null=True, default=None, verbose_name="Изделие",
                             on_delete=models.CASCADE)
    image = FilerImageField(null=True, blank=True, verbose_name="Изображение", on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False, verbose_name="Основное?")
    is_active = models.BooleanField(default=True, verbose_name="Активно?")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Создано")
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name="Обновленно")

    def __str__(self):
        return "%s" % (self.id)

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"