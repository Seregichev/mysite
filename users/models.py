# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import post_save

class Company(models.Model):
    short_name = models.CharField(max_length=128, blank=True, null=True, default=None,
                                  verbose_name=u"Сокращенное название")
    name = models.CharField(max_length=128, blank=True, null=True, default=None, verbose_name=u"Полное название")
    tax = models.DecimalField(max_digits=3, decimal_places=1, default=18.0, verbose_name=u"НДС [%]")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=u"Создано")
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=u"Обновленно")

    def __str__(self):
        return "%s" % (self.short_name)

    class Meta:
        verbose_name = u"Компания"
        verbose_name_plural = u"Компании"


class CustomUser(User):

    company = models.ForeignKey(Company, blank=True, null=True, default=None, verbose_name=u"Компания",
                             on_delete=models.CASCADE)

    objects = UserManager()


def create_custom_user(sender, instance, created, **kwargs):
    if created:
        values = {}
        for field in sender._meta.local_fields:
            values[field.attname] = getattr(instance, field.attname)
        user = CustomUser(**values)
        user.save()

post_save.connect(create_custom_user, User)