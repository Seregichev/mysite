# -*- coding: utf-8 -*-
from django.db import models
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from database_item.models import Item, ItemCategory
from decimal import Decimal
from .forms import CalcForm, CalcDriveForm, CalcNmb, CalcControlForm
from .formula import add_commute_drive_items_into_estimate


# Плагин настройки отображения плагина визализации подбора системы управления
@python_2_unicode_compatible
class CalcControlPluginSetting(CMSPlugin):

    type = models.CharField(_(u'Название поля типа управления'), max_length=64, null=True, blank=True,
                            default=_(u'Тип управления'))
    voltage = models.CharField(_(u'Название поля выбора напряжения'), max_length=64, null=True, blank=True,
                               default=_(u'Напряжение'))
    voltage_unit = models.CharField(_(u'Единица измерения напряжения'), max_length=64, null=True, blank=True,
                            default=_(u'[ В ]'))
    show_input_output = models.BooleanField(default=True, verbose_name=u"Показывать input поля входов/выходов")

    discret_input = models.CharField(_(u'Название поля дискретных входов'), max_length=64, null=True, blank=True,
                               default=_(u'Дискретные входы'))
    discret_output = models.CharField(_(u'Название поля дискретных выходов'), max_length=64, null=True, blank=True,
                               default=_(u'Дискретные выходы'))
    more = models.CharField(_(u'Название ссылки доп параметров'), max_length=64, null=True, blank=True,
                            default=_(u'Дополнительно'))
    manufacture_item = models.CharField(_(u'Приставка поля производителя комплектующих'), max_length=64, null=True,
                                        blank=True, default=_(u'Производитель'))
    series_item = models.CharField(_(u'Приставка серии комплектующих'), max_length=64, null=True,
                                        blank=True, default=_(u'Серия'))
    manufacture_relays = models.CharField(_(u'Приставка поля производителя промежуточных реле'), max_length=64, null=True, blank=True,
                                            default=_(u'Производитель промежуточных реле'))
    series_relays = models.CharField(_(u'Приставка поля серии промежуточных реле'), max_length=64, null=True, blank=True,
                                     default=_(u'Серия промежуточных реле'))
    manufacture_terminal = models.CharField(_(u'Приставка производителя клемм'), max_length=64, null=True, blank=True,
                                        default=_(u'Производитель клемм'))
    type_terminal = models.CharField(_(u'Приставка типа клемм'), max_length=64, null=True, blank=True,
                                            default=_(u'Тип клемм'))


    tag_class = models.CharField(_(u'HTML класс'), max_length=256, null=True, blank=True,)
    tag_style = models.CharField(_(u'HTML стиль'), max_length=256, null=True, blank=True)


# Плагин визализации подбора системы управления
@plugin_pool.register_plugin
class CalcControlPlugin(CMSPluginBase):

    module = _(u"Калькуляторы")
    name = _(u"Подбор системы управления")
    model = CalcControlPluginSetting
    render_template = "plugins/calc/calc_control.html"
    require_parent = True
    allow_children = True

    def render(self, context, instance, placeholder):
        form = CalcControlForm(context['request'].POST or None)
        context['calc_control'] = form

        context = super(CalcControlPlugin, self).render(context, instance, placeholder)

        request = context['request']

        if request.method == 'POST':

            if request.POST.get('calc_control', None):
                voltage = request.POST.get('calc_control_voltage', None)
                type = request.POST.get('calc_control_type', None)
                manufacturer = request.POST.get('calc_control_manufacturer', None)

                itemqueryset = Item.objects.filter(voltage__gte=voltage, is_active=True)

                if type == "PLC":
                    itemqueryset = itemqueryset.filter(category__in=ItemCategory.objects.get(name=u'ПЛК') \
                                                        .get_descendants(include_self=True))

                if type == "ProgrammableRelay":
                    itemqueryset = itemqueryset.filter(category__in=ItemCategory.objects.get(name=u'Программируемое реле') \
                                                       .get_descendants(include_self=True))

                if type == "Relay":
                    itemqueryset = itemqueryset.filter(category__in=ItemCategory.objects.get(name=u'Промежуточное реле') \
                                                        .get_descendants(include_self=True))


                if manufacturer:
                    itemqueryset = itemqueryset.filter(manufacturer__name=manufacturer, is_active=True)


                if not itemqueryset.filter(variables__contains=['discret_input']).exists():
                    context['calc_control'].fields['calc_control_discret_input'].disabled = True

                if not itemqueryset.filter(variables__contains=['discret_output']).exists():
                    context['calc_control'].fields['calc_control_discret_output'].disabled = True

                if not itemqueryset.filter(variables__contains=['fast_input']).exists():
                    context['calc_control'].fields['calc_control_fast_discret_input'].disabled = True

                if not itemqueryset.filter(variables__contains=['fast_output']).exists():
                    context['calc_control'].fields['calc_control_fast_discret_output'].disabled = True

                if not itemqueryset.filter(variables__contains=['analog_0_10V_input']).exists():
                    context['calc_control'].fields['calc_control_analog_0_10V_input'].disabled = True

                if not itemqueryset.filter(variables__contains=['analog_0_10V_output']).exists():
                    context['calc_control'].fields['calc_control_analog_0_10V_output'].disabled = True

                if not itemqueryset.filter(variables__contains=['analog_0_20mA_input']).exists():
                    context['calc_control'].fields['calc_control_analog_0_20mA_input'].disabled = True

                if not itemqueryset.filter(variables__contains=['analog_0_20mA_output']).exists():
                    context['calc_control'].fields['calc_control_analog_0_20mA_output'].disabled = True

                if not itemqueryset.filter(variables__contains=['analog_rtd_input']).exists():
                    context['calc_control'].fields['calc_control_analog_rtd_input'].disabled = True

                if not itemqueryset.filter(variables__contains=['profinet']).exists():
                    context['calc_control'].fields['calc_control_profinet'].disabled = True

                if not itemqueryset.filter(variables__contains=['profibus']).exists():
                    context['calc_control'].fields['calc_control_profibus'].disabled = True

                if not itemqueryset.filter(variables__contains=['profibus']).exists():
                    context['calc_control'].fields['calc_control_profibus'].disabled = True

                if not itemqueryset.filter(variables__contains=['modbus_tcp']).exists():
                    context['calc_control'].fields['calc_control_modbus_tcp'].disabled = True

                if not itemqueryset.filter(variables__contains=['modbus_rtu']).exists():
                    context['calc_control'].fields['calc_control_modbus_rtu'].disabled = True

        return context


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
    show_input_output = models.BooleanField(default=True, verbose_name=u"Показывать input поля входов/выходов")

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

            if request.POST.get('calc_drive', None):
                voltage = request.POST.get('calc_drive_voltage', None)
                power = request.POST.get('calc_drive_power', None)
                manufacturer = request.POST.get('calc_drive_manufacturer', None)

                current = ((Decimal(power) * Decimal(1000)) / (Decimal(voltage) * Decimal(settings.COSINE_PHI)))

                if manufacturer:
                    itemqueryset = Item.objects.filter(category__in=ItemCategory.objects.get(name=u'Силовая коммутация')\
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

# TODO: добавить при переносе функции добавления доп изделий управления
from django.db.models.expressions import RawSQL
from django.contrib import messages

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

            if settings.DEBUG:
                print(request.POST)

            if request.POST.get('calc_drive', None):
                add_commute_drive_items_into_estimate(request=request)

            if request.POST.get('calc_control', None):
                print("  ")
                print('Yes, the request from calc_control plugin is arrived')
                choised_discret_input = request.POST.get('calc_control_discret_input') or 0
                choised_discret_output = request.POST.get('calc_control_discret_output') or 0

                def select_control_items(request, items_list, one_var_name, one_var_value, compatibility_code,
                                         category__name, two_var_name="", two_var_value=0.0, places_list=None):
                    # items_list[][] - двумерный список отобранных изделий, в котором items_list[модель изделия][кол-во]

                    # получаем queryset изделий из запрашиваемой категории по коду совместимости
                    modules = Item.objects.filter(category__name=category__name,
                                                  compatibility_code=compatibility_code)

                    # сторожевая собака чтобы не зависнуть в цикле
                    watchdog = 0

                    # Переменная наличия ошибки при подборе
                    error = False

                    # открываем цикл, пока не подберем нужное колличество изделий с заданным кол-вом параметров
                    while one_var_value > 0 or two_var_value > 0 and watchdog < 1000:
                        watchdog +=1

                        # создаем первую выборку изделий
                        first_items = modules

                        # отсортировываем выборку на наличие запрашиваемых параметров
                        if one_var_value > 0:
                            first_items = first_items.filter(variables__contains=one_var_name)

                        if two_var_value > 0:
                            first_items = first_items.filter(variables__contains=two_var_name)

                        # переносим первую выборку во вторую
                        second_items = first_items

                        # фильтруем вторую выборку на условии меньше или равно искомому колличеству
                        # сортируем выборку по искомому параметру в порядке возрастания
                        if one_var_value > 0:
                            second_items = second_items.filter(variables__lte={one_var_name: one_var_value})
                            # способ сортировки по hstore полю в порядке возрастания
                            second_items = second_items.order_by(
                                RawSQL("Cast(variables->%s as Integer)", (one_var_name,)))

                        if two_var_value > 0:
                            second_items = second_items.filter(variables__lte={two_var_name: two_var_value})
                            second_items = second_items.order_by(
                                RawSQL("Cast(variables->%s as Integer)", (two_var_name,)))

                        # переносим вторую выборку в третью
                        third_items = second_items

                        # TODO: проверить работу or not third_items.exists() и при не нужности перенести для норм работы
                        # исключаем из выборки если кол-во запрашиваемых параметров подобрано или черезмерно подобрано
                        if one_var_value <= 0:
                            third_items = third_items.exclude(variables__contains=one_var_name)
                        if two_var_value <= 0:
                            third_items = third_items.exclude(variables__contains=two_var_name)

                        # запрашиваем на наличие изделий в выборке - если нет, то возвращаемся ко второй выборке изделий
                        if not third_items.exists():
                            third_items = second_items

                        # переносим выборку в итоговые изделия
                        items = third_items

                        # если изделия есть в выбоке то делаем порядковый реверс что бы подобранное изделий с максимально возможным параметром было первым в выдаче
                        if items:
                            items = items.reverse()

                        # если изделий нетб то возвращаемся к первой выборке и сортируем ее в порядке возрастания запрашиваемого параметра
                        else:
                            items = first_items
                            if one_var_value > 0:
                                items = items.order_by(RawSQL("Cast(variables->%s as Integer)", (one_var_name,)))
                            if two_var_value > 0:
                                items = items.order_by(RawSQL("Cast(variables->%s as Integer)", (two_var_name,)))

                        # Если и в этом случае нет изделий, прерываем цикл и выдаем сообщение об ошибке
                        if not items:
                            messages.info(request, u'Ошибка: невозможно выполнить подбор. Уменьшите заданные критерии.')
                            error = True
                            break

                        # получаем первое идущее в выборке изделие
                        item = items.first()

                        # если изделие присутствует и список подобранных изделий содержит первую позицию
                        if item and len(items_list):

                            # обнуляем счетчик цикла for
                            for_index = 0

                            # обходим циклом все доступные места и их названия для доп модулей
                            for place_name, place_value in places_list:
                                place_value = int(place_value)

                                # пытаемся получить Это место из изделия
                                try:
                                    if item.variables[place_name]:

                                        # если кол-во доступных мест установки больше 0, то
                                        if place_value > 0:
                                            # если в списке подобранных изделий последнее изделие не равно текущему подобранному изделию, то добавляем текущее подобранное изделие в список подобранных изделий
                                            if items_list[len(items_list) - 1][0] != item:
                                                items_list.append([item, 1])

                                            # иначе если текущее подобранное изделие есть в списке подобранных изделий то увеличиваем кол-во последнего изделия в списке подобранных изделий
                                            elif items_list[len(items_list) - 1][0] == item:
                                                items_list[len(items_list) - 1][1] += 1

                                            # пытаемся вычесть кол-во подобранных параметров из выбранного изделия
                                            if one_var_value > 0:
                                                try:
                                                    one_var_value -= int(item.variables[one_var_name])
                                                except (AttributeError, KeyError):
                                                    one_var_value = 0
                                                    messages.info(request,
                                                                  u'Ошибка: не возможно вычесть %s при подборе управления' % one_var_name)
                                                    error = True

                                            if two_var_value > 0:
                                                try:
                                                    two_var_value -= int(item.variables[two_var_name])
                                                except (AttributeError, KeyError):
                                                    two_var_value = 0
                                                    messages.info(request,
                                                                  u'Ошибка: не возможно вычесть %s при подборе управления' % two_var_name)
                                                    error = True

                                            # вычитаем кол-во Этих мест с изделия которое добавили
                                            place_value -= int(item.variables[place_name])
                                            # перезаписываем название и кол-во мест в списке мест
                                            places_list[for_index]=[place_name, place_value]

                                        # если кол-во доступных мест в изделии меньше или = 0, то исключаем из выборки module (перед циклом while) все изделия (модули) с таким требуемым расположением
                                        else:
                                            modules = modules.exclude(variables__contains=place_name)
                                            try:
                                                if items_list[len(items_list) - 1][0].variables[place_name]:
                                                    items_list.pop()
                                            except KeyError: None

                                # если при получении переменной hstore с именем запрашиваемого места расположения модуля происходит ошибка ключа (ключ не найден) то ничего не делаем и пропускаем выборку
                                except KeyError: None

                                for_index +=1

                    return request, items_list, one_var_value, two_var_value, error

                discret_input=round(int(choised_discret_input),0)
                discret_output = round(int(choised_discret_output),0)

                if settings.DEBUG:
                    messages.info(request, u'Запрашиваемые дискретные входа: %s, и выхода: %s ' % (discret_input, discret_output))

                items_list=[]
                index=0
                cpu = Item.objects.get(id=882)
                print('This is CPU:')
                places_list = []
                try: places_list.append(["left_places", cpu.variables["left_places"]])
                except KeyError: None
                try: places_list.append(["right_places", cpu.variables["right_places"]])
                except KeyError: None
                try: places_list.append(["board_places", cpu.variables["board_places"]])
                except KeyError: None

                print(places_list)
                for key, value in places_list:
                    print("key: %s, value: %s" % (key, value))

                print(cpu.variables["left_places"])
                print(' ')
                items_list.append([cpu, 1])

                request, items_list, discret_input, discret_output, \
                                                 error = select_control_items(request=request, items_list=items_list,
                                                                              one_var_name="discret_input",
                                                                              one_var_value=discret_input,
                                                                              compatibility_code=cpu.compatibility_code,
                                                                              category__name=u"Модуль расширения ПЛК",
                                                                              two_var_name="discret_output",
                                                                              two_var_value=discret_output,
                                                                              places_list=places_list
                                                                              )

                messages.info(request,
                              u'Осталось первого параметра %s, второго параметра %s' % (discret_input, discret_output))

                # TODO: удалить ниже следующее после пусконаладки
                print(items_list)
                print("  ")
                if settings.DEBUG:
                    for key, value in items_list:
                        messages.info(request, u'Изделие: %s, кол-во: %s ' % (key.name, value))

            if not request.POST._mutable:
                request.POST._mutable = True
                request.POST["comment"] = ''
                request.POST._mutable = False

        context = super(CalcFormPlugin, self).render(context, instance, placeholder)
        return context

# TODO: Перенести функцию добавления модулей управления в отдельный файл