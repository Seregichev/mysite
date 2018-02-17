# -*- coding: utf-8 -*-
from django.db import models
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from database_item.models import Item
from django.utils.encoding import python_2_unicode_compatible

# Плагин приветсвия
@python_2_unicode_compatible
class HelloPluginSetting(CMSPlugin):
    welcome = models.CharField(_(u'Приветсвие'), max_length=128, null=True, blank=True)
    afterword = models.TextField(_(u'Послесовие'), max_length=256, null=True, blank=True)
    unnamed_name = models.CharField(_(u'Имя неавторизованного'), max_length=128, null=True, blank=True)
    tag_class = models.CharField(_(u'HTML класс'), max_length=256, null=True, blank=True)
    tag_style = models.CharField(_(u'HTML стиль'), max_length=256, null=True, blank=True)

    def get_title(self):
        return self.welcome or self.afterword

    def __str__(self):
        return self.get_title()


@plugin_pool.register_plugin
class HelloPlugin(CMSPluginBase):

    module = _("Plugins")
    name = _("Hello Plugin")
    model = HelloPluginSetting
    render_template = "plugins/hello_plugin.html"

