# -*- coding: utf-8 -*-
from django.db import models
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from .forms import CalcForm, CalcDriveForm
from .formula import *
from database_item.models import ItemCategory

# Плагин визализации силовой коммутации привода
@python_2_unicode_compatible
class CalcDrivePluginSetting(CMSPlugin):

    type = models.CharField(_(u'Название поля выбора типа коммутации'), max_length=64, null=True, blank=True,
                            default=_(u'Тип пуска'))
    voltage = models.CharField(_(u'Название поля выбора напряжения'), max_length=16, null=True, blank=True,
                               default=_(u'Напряжение'))
    voltage_unit = models.CharField(_(u'Единица измерения напряжения'), max_length=16, null=True, blank=True,
                            default=_(u'[ В ]'))
    power = models.CharField(_(u'Название поля выбора мощности'), max_length=16, null=True, blank=True,
                               default=_(u'Мощность'))
    power_unit = models.CharField(_(u'Единица измерения мощности'), max_length=16, null=True, blank=True,
                             default=_(u'[ кВт ]'))
    more = models.CharField(_(u'Название ссылки доп параметров'), max_length=64, null=True, blank=True,
                            default=_(u'Дополнительно'))
    atribute = models.CharField(_(u'Приставка атрибутов'), max_length=64, null=True, blank=True,
                            default=_(u'Интерфейс'))
    manufacture_item = models.CharField(_(u'Приставка производителя комплектующих'), max_length=64, null=True,
                                        blank=True, default=_(u'Производитель'))
    manufacture_terminal = models.CharField(_(u'Приставка производителя клемм'), max_length=64, null=True, blank=True,
                                        default=_(u'Клеммы'))

    tag_class = models.CharField(_(u'HTML класс'), max_length=256, null=True, blank=True,)
    tag_style = models.CharField(_(u'HTML стиль'), max_length=256, null=True, blank=True)


@plugin_pool.register_plugin
class CalcDrivePlugin(CMSPluginBase):

    module = _(u"Калькуляторы")
    name = _(u"Коммутация привода")
    model = CalcDrivePluginSetting
    render_template = "plugins/calc/calc_drive.html"
    require_parent = True

    def render(self, context, instance, placeholder):
        context['commute_drive'] = CalcDriveForm(context['request'].POST or None)
        context = super(CalcDrivePlugin, self).render(context, instance, placeholder)
        return context

# Плагин добавления кнопки отправки формы
@python_2_unicode_compatible
class CalcSubmitPluginSetting(CMSPlugin):
    name = models.CharField(_(u'Название'), max_length=32, null=True, blank=True, default=_(u'Отправить'))
    button_class = models.CharField(_(u'HTML класс кнопки'), max_length=256, null=True, blank=True, default='btn btn-primary')
    button_style = models.CharField(_(u'HTML стиль кнопки'), max_length=256, null=True, blank=True)
    tag_class = models.CharField(_(u'HTML класс div'), max_length=256, null=True, blank=True, default='form-group')
    tag_style = models.CharField(_(u'HTML стиль div'), max_length=256, null=True, blank=True)

@plugin_pool.register_plugin
class CalcSubmitPlugin(CMSPluginBase):
    module = _(u"Калькуляторы")
    name = _(u"Кнопка отправки формы")
    model = CalcSubmitPluginSetting
    render_template = "plugins/calc/calc_submit.html"
    require_parent = True

    def render(self, context, instance, placeholder):
        context = super(CalcSubmitPlugin, self).render(context, instance, placeholder)
        return context

# Плагин добавления формы расчета и добавления в смету
@python_2_unicode_compatible
class CalcFormPluginSetting(CMSPlugin):
    comment = models.CharField(_(u'Приставка назначения'), max_length=64, null=True, blank=True, default=_(u'Привод'))

    tag_class = models.CharField(_(u'HTML класс'), max_length=256, null=True, blank=True)
    tag_style = models.CharField(_(u'HTML стиль'), max_length=256, null=True, blank=True)

    def get_title(self):
        return self.comment

    def __str__(self):
        return self.get_title()

@plugin_pool.register_plugin
class CalcFormPlugin(CMSPluginBase):

    module = _(u"Калькуляторы")
    name = _(u"Форма")
    model = CalcFormPluginSetting
    render_template = "plugins/calc/calc_form.html"
    allow_children = True

    def render(self, context, instance, placeholder):

        context['form'] = CalcForm(context['request'].POST or None)

        request = context['request']
        if request.method == 'POST':
            data = request.POST
            print(data)


            user = request.user

            if data["calc_drive"] == '1':
                add_commute_drive_items_into_estimate(user=user, request=request)

            if not request.POST._mutable:
                request.POST._mutable = True

            request.POST["comment"] = ''


        context = super(CalcFormPlugin, self).render(context, instance, placeholder)
        return context