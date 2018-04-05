# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from .views import check_fields_in_calculator

urlpatterns = [
    url(r'check_fields_in_calculator/', check_fields_in_calculator, name='check_fields_in_calculator'),
]
