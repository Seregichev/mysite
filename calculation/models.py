# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from database_item.models import Item
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class Calculate(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.CASCADE, verbose_name="Пользователь")
    calculate_name = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Название")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Итого")  # total price in calculate
    comments = models.TextField(blank=True, null=True, default=None, verbose_name="Комментарий")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Создано")
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name="Обновлено")

    def __str__(self):
        return u"Расчет %s" % (self.calculate_name)

    class Meta:
        verbose_name = u"Расчет"
        verbose_name_plural = u"Расчеты"

    def save(self, *args, **kwargs):
        super(Calculate, self).save(*args, **kwargs)

@python_2_unicode_compatible
class ItemInCalculate(models.Model):
    uuid_id = models.UUIDField(blank=False, null=True, default=None)
    comment = models.CharField(max_length=128, blank=True, null=True, default=None)
    calculate = models.ForeignKey(Calculate, blank=True, null=True, default=None, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, blank=True, null=True, default=None, on_delete=models.CASCADE)
    nmb = models.IntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0) #price_per_item * nmb
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return u"%s" % self.item.name

    class Meta:
        verbose_name = u"Изделие в расчете"
        verbose_name_plural = u"Изделие в расчете"

    def save(self, *args, **kwargs):
        price_per_item = self.item.price
        self.price_per_item = price_per_item
        self.total_price = int(self.nmb) * self.price_per_item

        super(ItemInCalculate, self).save(*args, **kwargs)

@python_2_unicode_compatible
class ItemInEstimate(models.Model):
    uuid_id = models.UUIDField(blank=False, null=True, default=None)
    comment = models.CharField(max_length=128, blank=True, null=True, default=None)
    item = models.ForeignKey(Item, blank=True, null=True, default=None, on_delete=models.CASCADE)
    nmb = models.IntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0) #price_per_item * nmb
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.CASCADE,
                             verbose_name="Пользователь")
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.item.name

    class Meta:
        verbose_name = u"Изделие в смете"
        verbose_name_plural = u"Изделия в смете"

    def save(self, *args, **kwargs):
        price_per_item = self.item.price
        self.price_per_item = price_per_item
        self.total_price = int(self.nmb) * self.price_per_item

        super(ItemInEstimate, self).save(*args, **kwargs)


def item_in_calculate_post_save(sender,instance,created,**kwargs):
    calculate = instance.calculate
    all_item_in_calculate = ItemInCalculate.objects.filter(calculate=calculate, is_active=True)

    calculate_total_price = 0
    for item in all_item_in_calculate:
        calculate_total_price += item.total_price

    instance.calculate.total_price = calculate_total_price
    instance.calculate.save(force_update=True)

post_save.connect(item_in_calculate_post_save, sender=ItemInCalculate)
