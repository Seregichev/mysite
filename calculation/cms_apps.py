# -*- coding: utf-8 -*-
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
gettext = lambda s: s

@apphook_pool.register  # register the application
class CalculationApphook(CMSApp):
    app_name = 'calculation'
    name = gettext('Расчеты')

    def get_urls(self, page=None, language=None, **kwargs):
        return ["calculation.urls_calculation"]

@apphook_pool.register  # register the application
class EstimateApphook(CMSApp):
    app_name = 'estimate'
    name = gettext('Смета')

    def get_urls(self, page=None, language=None, **kwargs):
        return ["calculation.urls_estimate"]