# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from .views import check_calc_drive_fields, check_calc_control_fields

urlpatterns = [
    url(r'check_calc_drive_fields/', check_calc_drive_fields, name='check_calc_drive_fields'),
    url(r'check_calc_control_fields/', check_calc_control_fields, name='check_calc_control_fields'),
]
