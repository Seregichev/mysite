# -*- coding: utf-8 -*-
from django.db import models
from django_hstore import hstore
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.encoding import python_2_unicode_compatible
from decimal import Decimal
from tinymce.models import HTMLField
from filer.fields.image import FilerImageField

TYPE_CURRENT_CHOICES = (
    ('AC', 'AC'),
    ('DC', 'DC')
)
TYPE_PROTECT_CLASS = (
    ('10', '10'),
    ('20', '20'),
    ('30', '30'),
    ('40', '40'),
)
TYPE_CURRENCY = (
    ('RUB', '₽'),
    ('USD', '$'),
    ('EUR', '€')
)

@python_2_unicode_compatible
class ItemCategory(MPTTModel):
    name = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name=u"Название")
    parent = TreeForeignKey('self', null=True, blank=True, default=None, related_name='children', verbose_name=u"Родитель", db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        verbose_name = u"Категория изделия"
        verbose_name_plural = u"Категории изделий"

@python_2_unicode_compatible
class ItemManufacturer(models.Model):
    short_name = models.CharField(max_length=5, blank=True, null=True, default=None, verbose_name=u"Сокращение")
    name = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name=u"Название")

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = u"Производитель изделия"
        verbose_name_plural = u"Производители изделий"

@python_2_unicode_compatible
class Item(models.Model):
    category = models.ForeignKey(ItemCategory, blank=True, null=True, default=None, verbose_name=u"Категория",
                                 on_delete=models.DO_NOTHING)
    manufacturer = models.ForeignKey(ItemManufacturer, blank=True, null=True, default=None,
                                     verbose_name=u"Производитель", on_delete=models.DO_NOTHING)
    series = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name=u"Серия")
    name = models.CharField(max_length=256, blank=True, null=True, default=None, verbose_name=u"Название")
    vendor_code = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name=u"Артикул")
    compatibility_code = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name=u"Код совместимости")
    description = HTMLField(blank=True, null=True, default=None, verbose_name=u"Описание")

    voltage = models.DecimalField(max_digits=7, decimal_places=0, default=0, verbose_name=u"Напряжение [В]")
    current = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name=u"Ток [А]")
    type_current = models.CharField(choices=TYPE_CURRENT_CHOICES, max_length=3, blank=True, null=True, default='AC',
                                    verbose_name=u"Вид тока")
    power = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name=u"Мощность [кВт]")

    height = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=u"Высота [мм]")
    width = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=u"Ширина [мм]")
    depth = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=u"Глубина [мм]")
    area = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=u"Площадь [мм^2]")

    variables = hstore.DictionaryField(blank=True, null=True, default=dict, db_index=True, verbose_name=u"Переменные")

    objects = hstore.HStoreManager()

    is_active = models.BooleanField(default=True, verbose_name=u"Активность")

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=u"Цена")
    currency = models.CharField(choices=TYPE_CURRENCY, max_length=3, blank=True, null=True, default='EUR',
                                    verbose_name=u"Валюта")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=u"Создано")
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=u"Обновленно")

    def __str__(self):
        return "%s, %s" % (self.vendor_code, self.name)

    class Meta:
        verbose_name = u"Изделие"
        verbose_name_plural = u"Изделия"

    def save(self, *args, **kwargs):
        if self.height > 0 and self.width and self.area == 0:
            self.area = self.height * self.width
        if self.type_current == 'AC':
            if self.current > 0 and self.power == 0:
                self.power = (self.voltage * self.current * Decimal('0.81')) / 1000
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
    item = models.ForeignKey(Item, blank=True, null=True, default=None, verbose_name=u"Изделие",
                             on_delete=models.CASCADE)
    image = FilerImageField(null=True, blank=True, verbose_name=u"Изображение", on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False, verbose_name=u"Основное")
    is_active = models.BooleanField(default=True, verbose_name=u"Активное")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=u"Создано")
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=u"Обновленно")

    def __str__(self):
        return "%s" % (self.id)

    class Meta:
        verbose_name = u"Изображение"
        verbose_name_plural = u"Изображения"

# Клас дополнительных изделий, нужен для подбора дополнительных изделий обязательных и необязательных
@python_2_unicode_compatible
class AddItem(models.Model):
    main_item = models.ForeignKey(Item, blank=True, null=True, default=None, verbose_name=u"Основное изделие",
                                  related_name="main_item", on_delete=models.CASCADE)
    adding_item = models.ForeignKey(Item, blank=True, null=True, default=None, verbose_name=u"Дополнительное изделие",
                                    related_name="adding_item", on_delete=models.CASCADE)
    nmb = models.IntegerField(default=1, verbose_name=u"Колличество",
                              help_text=u"Колличество штук обязательных при добавлении")

    def __str__(self):
        return "%s" % (self.adding_item)

    class Meta:
        unique_together = ("main_item", "adding_item")
        verbose_name = u"Связанное изделие"
        verbose_name_plural = u"Связанные изделия"