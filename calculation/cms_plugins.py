# -*- coding: utf-8 -*-
from django.db import models
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from .forms import CalcForm, CalcDriveForm, CalcNmb
from .formula import add_commute_drive_items_into_estimate
from django.conf import settings
from django.http import JsonResponse
from database_item.models import Item, ItemCategory
from decimal import Decimal


# Плагин настройки отображения плагина визализации силовой коммутации привода
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
    series_item = models.CharField(_(u'Приставка серии комплектующих'), max_length=64, null=True,
                                        blank=True, default=_(u'Серия'))
    manufacture_terminal = models.CharField(_(u'Приставка производителя клемм'), max_length=64, null=True, blank=True,
                                        default=_(u'Производитель клемм'))
    type_terminal = models.CharField(_(u'Приставка типа клемм'), max_length=64, null=True, blank=True,
                                            default=_(u'Тип клемм'))

    tag_class = models.CharField(_(u'HTML класс'), max_length=256, null=True, blank=True,)
    tag_style = models.CharField(_(u'HTML стиль'), max_length=256, null=True, blank=True)


# Плагин визализации силовой коммутации привода
@plugin_pool.register_plugin
class CalcDrivePlugin(CMSPluginBase):

    module = _(u"Калькуляторы")
    name = _(u"Коммутация привода")
    model = CalcDrivePluginSetting
    render_template = "plugins/calc/calc_drive.html"
    require_parent = True
    allow_children = True

    def render(self, context, instance, placeholder):
        form = CalcDriveForm(context['request'].POST or None)
        context['commute_drive'] = form
        context = super(CalcDrivePlugin, self).render(context, instance, placeholder)

        request = context['request']

        # Проверка форм на наличие атрибутов в изделиях

        if request.method == 'POST':
            data = request.POST

            voltage = data['calc_drive_voltage'] or None
            power = data['calc_drive_power'] or None
            manufacturer = data['calc_drive_manufacturer'] or None

            current = ((Decimal(power) * Decimal(1000)) / (Decimal(voltage) * Decimal(settings.COSINE_PHI)))

            if manufacturer:
                itemqueryset = Item.objects.filter(category__in=ItemCategory.objects.get(name=u'Силовая коммутация') \
                                                   .get_descendants(include_self=True),
                                                   current__gte=current, voltage__gte=voltage,
                                                   manufacturer__name=manufacturer, is_active=True)
            else:
                itemqueryset = Item.objects.filter(category__in=ItemCategory.objects.get(name=u'Силовая коммутация')\
                                                                 .get_descendants(include_self=True),
                                                   current__gte=current, voltage__gte=voltage, is_active=True)

            if not itemqueryset.filter(variables__contains=['discret_input']).exists():
                context['commute_drive'].fields['calc_drive_discret_input'].disabled = True

            if not itemqueryset.filter(variables__contains=['discret_output']).exists():
                context['commute_drive'].fields['calc_drive_discret_output'].disabled = True

            if not itemqueryset.filter(variables__contains=['analog_input']).exists():
                context['commute_drive'].fields['calc_drive_analog_input'].disabled = True

            if not itemqueryset.filter(variables__contains=['analog_output']).exists():
                context['commute_drive'].fields['calc_drive_analog_output'].disabled = True

            if not itemqueryset.filter(variables__contains=['profinet']).exists():
                context['commute_drive'].fields['calc_drive_profinet'].disabled = True

            if not itemqueryset.filter(variables__contains=['profibus']).exists():
                context['commute_drive'].fields['calc_drive_profibus'].disabled = True

            if not itemqueryset.filter(variables__contains=['rs485']).exists():
                context['commute_drive'].fields['calc_drive_rs485'].disabled = True

        return context


# Плагин настройки отображения плагина добавления кнопки отправки формы
@python_2_unicode_compatible
class CalcSubmitPluginSetting(CMSPlugin):
    name = models.CharField(_(u'Название'), max_length=32, null=True, blank=True, default=_(u'Отправить'))
    button_class = models.CharField(_(u'HTML класс кнопки'), max_length=256, null=True, blank=True, default='btn btn-primary')
    button_style = models.CharField(_(u'HTML стиль кнопки'), max_length=256, null=True, blank=True)
    tag_class = models.CharField(_(u'HTML класс div'), max_length=256, null=True, blank=True, default='form-group')
    tag_style = models.CharField(_(u'HTML стиль div'), max_length=256, null=True, blank=True)


# Плагин настройки отображения плагина добавления кнопки отправки формы
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

# Плагин настройки отображения плагина ввода количества
@python_2_unicode_compatible
class CalcNmbPluginSetting(CMSPlugin):
    name = models.CharField(_(u'Название'), max_length=32, null=True, blank=True, default=_(u'Колличество'))
    tag_class = models.CharField(_(u'HTML класс div'), max_length=256, null=True, blank=True, default='form-group input-group')
    tag_style = models.CharField(_(u'HTML стиль div'), max_length=256, null=True, blank=True)

# Плагин настройки отображения плагина ввода количества
@plugin_pool.register_plugin
class CalcNmbPlugin(CMSPluginBase):
    module = _(u"Калькуляторы")
    name = _(u"Колличество для расчета")
    model = CalcNmbPluginSetting
    render_template = "plugins/calc/calc_nmb.html"
    require_parent = True

    def render(self, context, instance, placeholder):
        form = CalcNmb(context['request'].POST or None)
        context['form_calc_nmb'] = form
        context = super(CalcNmbPlugin, self).render(context, instance, placeholder)
        return context

# Плагин настройки отображения плагина добавления самой формы расчета и отправки в смету
@python_2_unicode_compatible
class CalcFormPluginSetting(CMSPlugin):
    comment = models.CharField(_(u'Приставка назначения'), max_length=64, null=True, blank=True, default=_(u'Привод'))

    tag_class = models.CharField(_(u'HTML класс'), max_length=256, null=True, blank=True)
    tag_style = models.CharField(_(u'HTML стиль'), max_length=256, null=True, blank=True)

    def get_title(self):
        return self.comment

    def __str__(self):
        return self.get_title()


# Плагин добавления самой формы расчета и отправки в смету
@plugin_pool.register_plugin
class CalcFormPlugin(CMSPluginBase):

    module = _(u"Калькуляторы")
    name = _(u"Форма")
    model = CalcFormPluginSetting
    render_template = "plugins/calc/calc_form.html"
    allow_children = True


    def render(self, context, instance, placeholder):

        form = CalcForm(context['request'].POST or None)
        context['form'] = form

        request = context['request']

        if request.method == 'POST':
            data = request.POST

            if settings.DEBUG:
                print(data)

            if data["calc_drive"] == '1':
                add_commute_drive_items_into_estimate(request=request)

            if not request.POST._mutable:
                request.POST._mutable = True
                request.POST["comment"] = ''
                request.POST._mutable = False

        context = super(CalcFormPlugin, self).render(context, instance, placeholder)
        return context