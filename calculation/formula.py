# -*- coding: utf-8 -*-
from .models import ItemInEstimate
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from uuid import uuid4
from database_item.models import ItemCategory, Item
from decimal import Decimal
from django.conf import settings
from django.db.models.expressions import RawSQL

# функция добавления изделия в смету или выдачи ошибки
def created_item_in_estimate(request, user,  uuid_id, item_id, is_active, nmb, comment, input_query=None):
    created = ItemInEstimate.objects.create(uuid_id=uuid_id, user=user, item_id=item_id,
                                            is_active=is_active, nmb=nmb, comment=comment,
                                            input_query=input_query)
    if created:
        if settings.DEBUG:
            messages.info(request, u'Изделие %s %s добавлено.' % (str(created.item.manufacturer.name), str(created.item.name)))
    else:
        messages.error(request, u'Невозможно добавить изделие в смету. Обратитесь в тех.поддержку')

    return created, request


# функция удаления из сметы всех изделий по совпадению uuid
def delete_uuid_id_in_estimate(request, user, uuid_id):
    delete_items = ItemInEstimate.objects.filter(uuid_id=uuid_id, user=user)
    if settings.DEBUG:
        messages.warning(request, u'"%s" из сметы удален.' % delete_items.values_list('comment').first())
    delete_items.delete()

    return request


# Функция добавления в смету изделий коммутации привода
def add_commute_drive_item(request, category, manufacturer, current, voltage, user, uuid_id, nmb, comment,
                           series=None, max_current=None,
                           check=True, manufacturer_filter_is_required=False,):

    item = Item.objects.filter(category=category, current__gte=current, voltage__gte=voltage, is_active=True)

    item = item.filter(variables__gte={'power_input': 3, 'power_output': 3})

    if max_current:
        item = item.filter(variables__gte={'max_current': max_current})

    if manufacturer_filter_is_required:
        if manufacturer:
            item = item.filter(manufacturer__name=manufacturer)
    else:
        if manufacturer and item.filter(manufacturer__name=manufacturer).exists():
            item = item.filter(manufacturer__name=manufacturer)

    if series:
        item = item.filter(series__contains=series)

    item = item.first()

    if item:
        # добавляем устройство в смету
        created, request = created_item_in_estimate(request=request, user=user, uuid_id=uuid_id,
                                                         item_id=item.id, is_active=True, nmb=nmb, comment=comment,
                                                         input_query={'category': category.id,'current': str(current),
                                                                      'voltage': str(voltage)})
        if created:
            for adding_item in Item.objects.filter(id=created.item_id).values(
                    'main_item__adding_item', 'main_item__nmb'):
                if adding_item.get('main_item__adding_item'):
                    created_item_in_estimate(request=request, user=user, uuid_id=uuid_id,
                                             item_id=adding_item.get('main_item__adding_item'),
                                             is_active=True, nmb=adding_item.get('main_item__nmb') * nmb,
                                             comment=comment)

        # Получение полей добавленного изделия
        try:
            item.discret_input = int(item.variables['discret_input'])
        except KeyError:
            item.discret_input = 0

        try:
            item.discret_output = int(item.variables['discret_output'])
        except KeyError:
            item.discret_output = 0

        try:
            item.analog_input = int(item.variables['analog_input'])
        except KeyError:
            item.analog_input = 0

        try:
            item.analog_output = int(item.variables['analog_output'])
        except KeyError:
            item.analog_output = 0

        try:
            item.profinet = int(item.variables['profinet'])
        except KeyError:
            item.profinet = 0

        try:
            item.profibus = int(item.variables['profibus'])
        except KeyError:
            item.profibus = 0

        try:
            item.rs485 = int(item.variables['rs485'])
        except KeyError:
            item.rs485 = 0

    else:
        # Если проверка включена то удаляем из сметы все изделия по uuid
        if check:
            request = delete_uuid_id_in_estimate(request=request, user=user, uuid_id=uuid_id)
            messages.warning(request, u'Изделие не найдено.')
        else:
            if settings.DEBUG:
                messages.info(request, u'Проверка отключена. Изделие не найдено.')

    return request, item


# Функция добавления в смету с доп полями сооветсвующими по коду соответсвия
def add_extra_item(request, category_in, manufacturer, user, uuid_id, nmb, comment, compatibility_code,
                   exclude_variables_name, variables_name, variables_key=1,
                   check=True, manufacturer_filter_is_required=False,):

    item = Item.objects.filter(category__in=ItemCategory.objects.get(id=category_in.id).get_descendants(include_self=True),
                               compatibility_code=compatibility_code, is_active=True)

    item = item.exclude(variables__contains=[exclude_variables_name])

    if manufacturer_filter_is_required:
        if manufacturer:
            item = item.filter(manufacturer__name=manufacturer)
    else:
        if manufacturer and item.filter(manufacturer__name=manufacturer).exists():
            item = item.filter(manufacturer__name=manufacturer)

    item = item.filter(variables__gte={variables_name: variables_key})

    item = item.first()

    if item:
        # добавляем устройство в смету
        created, request = created_item_in_estimate(request=request, user=user, uuid_id=uuid_id,
                                                         item_id=item.id, is_active=True, nmb=nmb, comment=comment,
                                                         input_query={'compatibility_code': compatibility_code,
                                                                      variables_key: variables_key})
        if created:
            for adding_item in Item.objects.filter(id=created.item_id).values(
                    'main_item__adding_item', 'main_item__nmb'):
                if adding_item.get('main_item__adding_item'):
                    created_item_in_estimate(request=request, user=user, uuid_id=uuid_id,
                                             item_id=adding_item.get('main_item__adding_item'),
                                             is_active=True, nmb=adding_item.get('main_item__nmb') * nmb,
                                             comment=comment)

        # Получение полей добавленного изделия
        try:
            item.discret_input = int(item.variables['discret_input'])
        except KeyError:
            item.discret_input = 0

        try:
            item.discret_output = int(item.variables['discret_output'])
        except KeyError:
            item.discret_output = 0

        try:
            item.analog_input = int(item.variables['analog_input'])
        except KeyError:
            item.analog_input = 0

        try:
            item.analog_output = int(item.variables['analog_output'])
        except KeyError:
            item.analog_output = 0

        try:
            item.profinet = int(item.variables['profinet'])
        except KeyError:
            item.profinet = 0

        try:
            item.profibus = int(item.variables['profibus'])
        except KeyError:
            item.profibus = 0

        try:
            item.rs485 = int(item.variables['rs485'])
        except KeyError:
            item.rs485 = 0


    else:
        # Если проверка включена то удаляем из сметы все изделия по uuid
        if check:
            request = delete_uuid_id_in_estimate(request=request, user=user, uuid_id=uuid_id)
            messages.warning(request, u'Изделие не найдено.')
        else:
            if settings.DEBUG:
                messages.info(request, u'Проверка отключена. Изделие не найдено.')


    return request, item

# функция добавления изделий коммутации привода в смету
def add_commute_drive_items_into_estimate(request):
    data = request.POST
    user = request.user

    # создаем уникальный идентификатор
    uuid_id = uuid4()

    # Выгружаем данные из посылки
    comment = u'Привод '+data["comment"]
    choise_voltage = data["calc_drive_voltage"]
    choise_power = data["calc_drive_power"]
    choise_type = data["calc_drive_type"]
    choise_manufacturer = data.get('calc_drive_manufacturer') or None
    choise_series = data.get('calc_drive_series') or None
    choise_manufacturer_terminals = data.get('calc_drive_manufacturer_terminals') or None
    choise_reverse = data.get('calc_drive_reverse') or None
    choise_bypass = data.get('calc_drive_bypass') or None
    choise_discret_input = int(data.get('calc_drive_discret_input') or 1)
    choise_discret_output = int(data.get('calc_drive_discret_output') or 1)
    choise_analog_input = int(data.get('calc_drive_analog_input') or 0)
    choise_analog_output = int(data.get('calc_drive_analog_output') or 0)
    choise_profinet = int(data.get('calc_drive_profinet') or 0)
    choise_profibus = int(data.get('calc_drive_profibus') or 0)
    choise_rs485 = int(data.get('calc_drive_rs485') or 0)
    choise_type_terminals = data.get('calc_drive_type_terminals') or None

    # Получаем колличество или ставим его равным 1
    choise_nmb = data.get('calc_nmb') or 1
    if choise_nmb == '0' or int(choise_nmb) < 0:
        choise_nmb = 1

    # формула расчета тока по мощности и напряжению для подбора коммутации привода
    current =((Decimal(choise_power) * Decimal(1000)) / (Decimal(choise_voltage) * Decimal(settings.COSINE_PHI)))

    if settings.DEBUG:
        messages.info(request, u'Расчетный ток: %s А.' % current)

    # получаем категории из списка категорий
    Category_Disconnector = ItemCategory.objects.filter(name__startswith='Рубильник').first()
    Category_CircuitBreaker = ItemCategory.objects.filter(name__startswith='Автоматический выключатель').first()
    Category_Contactor = ItemCategory.objects.filter(name__startswith='Контактор').first()
    Category_FreqConverter = ItemCategory.objects.filter(name__startswith='Частотный преобразователь').first()
    Category_SoftStarter = ItemCategory.objects.filter(name__startswith='Устройство плавного пуска').first()
    Category_TermRele = ItemCategory.objects.filter(name__startswith='Тепловое реле').first()

    created_item = None

    if choise_type == 'Streight':
        request, created_item = add_commute_drive_item(request, category=Category_TermRele,
                                                       manufacturer=choise_manufacturer, current=current,
                                                       series=choise_series,
                                                       max_current=float(current) * 0.63,
                                                       voltage=choise_voltage, user=user, uuid_id=uuid_id,
                                                       nmb=choise_nmb,
                                                       manufacturer_filter_is_required=True,
                                                       comment=comment)

    elif choise_type == 'SoftStart':
        request, created_item = add_commute_drive_item(request, category=Category_SoftStarter,
                                                       manufacturer=choise_manufacturer, current=current,
                                                       series=choise_series,
                                                       voltage=choise_voltage, user=user, uuid_id=uuid_id,
                                                       manufacturer_filter_is_required=True,
                                                       nmb=choise_nmb, comment=comment)

        if created_item.discret_input < choise_discret_input:
            request, created_extra_item = add_extra_item(request=request, category_in=Category_FreqConverter,
                                                   manufacturer=created_item.manufacturer, user=user, uuid_id=uuid_id,
                                                   nmb=choise_nmb, comment=comment,
                                                   compatibility_code=created_item.compatibility_code,
                                                   variables_name='discret_input', variables_key=choise_discret_input,
                                                   exclude_variables_name='power_input',
                                                   check=True, manufacturer_filter_is_required=True)

        if created_item.discret_output < choise_discret_output:
            request, created_extra_item = add_extra_item(request=request, category_in=Category_FreqConverter,
                                                   manufacturer=created_item.manufacturer, user=user, uuid_id=uuid_id,
                                                   nmb=choise_nmb, comment=comment,
                                                   compatibility_code=created_item.compatibility_code,
                                                   variables_name='discret_output',
                                                   variables_key=choise_discret_output,
                                                   exclude_variables_name='power_input',
                                                   check=True, manufacturer_filter_is_required=True)

    elif choise_type == 'FreqConvert':
        request, created_item = add_commute_drive_item(request, category=Category_FreqConverter,
                                                       manufacturer=choise_manufacturer, current=current,
                                                       series=choise_series,
                                                       voltage=choise_voltage, user=user, uuid_id=uuid_id,
                                                       manufacturer_filter_is_required=True,
                                                       nmb=choise_nmb, comment=comment)

        if created_item.profinet < choise_profinet:
            request, created_extra_item = add_extra_item(request=request, category_in=Category_FreqConverter,
                                     manufacturer=created_item.manufacturer, user=user, uuid_id=uuid_id,
                                     nmb=choise_nmb, comment=comment,
                                     compatibility_code=created_item.compatibility_code,
                                     variables_name='profinet',
                                     variables_key=choise_profinet,
                                     exclude_variables_name='power_input',
                                     check=True, manufacturer_filter_is_required=True)
        elif created_item.profibus < choise_profibus:
            request, created_extra_item = add_extra_item(request=request, category_in=Category_FreqConverter,
                                     manufacturer=created_item.manufacturer, user=user, uuid_id=uuid_id,
                                     nmb=choise_nmb, comment=comment,
                                     compatibility_code=created_item.compatibility_code,
                                     variables_name='profibus',
                                     variables_key=choise_profibus,
                                     exclude_variables_name='power_input',
                                     check=True, manufacturer_filter_is_required=True)
        elif created_item.rs485 < choise_rs485:
            request, created_extra_item = add_extra_item(request=request, category_in=Category_FreqConverter,
                                     manufacturer=created_item.manufacturer, user=user, uuid_id=uuid_id,
                                     nmb=choise_nmb, comment=comment,
                                     compatibility_code=created_item.compatibility_code,
                                     variables_name='rs485',
                                     variables_key=choise_rs485,
                                     exclude_variables_name='power_input',
                                     check=True, manufacturer_filter_is_required=True)
        elif created_item.analog_input < choise_analog_input:
            request, created_extra_item = add_extra_item(request=request, category_in=Category_FreqConverter,
                                     manufacturer=created_item.manufacturer, user=user, uuid_id=uuid_id,
                                     nmb=choise_nmb, comment=comment,
                                     compatibility_code=created_item.compatibility_code,
                                     variables_name='analog_input',
                                     variables_key=choise_analog_input,
                                     exclude_variables_name='power_input',
                                     check=True, manufacturer_filter_is_required=True)
        elif created_item.analog_output < choise_analog_output:
            request, created_extra_item = add_extra_item(request=request, category_in=Category_FreqConverter,
                                     manufacturer=created_item.manufacturer, user=user, uuid_id=uuid_id,
                                     nmb=choise_nmb, comment=comment,
                                     compatibility_code=created_item.compatibility_code,
                                     variables_name='analog_output',
                                     variables_key=choise_analog_output,
                                     exclude_variables_name='power_input',
                                     check=True, manufacturer_filter_is_required=True)
        elif created_item.discret_input < choise_discret_input:
            request, created_extra_item = add_extra_item(request=request, category_in=Category_FreqConverter,
                                     manufacturer=created_item.manufacturer, user=user, uuid_id=uuid_id,
                                     nmb=choise_nmb, comment=comment,
                                     compatibility_code=created_item.compatibility_code,
                                     variables_name='discret_input', variables_key=choise_discret_input,
                                     exclude_variables_name='power_input',
                                     check=True, manufacturer_filter_is_required=True)
        elif created_item.discret_output < choise_discret_output:
            request, created_extra_item = add_extra_item(request=request, category_in=Category_FreqConverter,
                                     manufacturer=created_item.manufacturer, user=user, uuid_id=uuid_id,
                                     nmb=choise_nmb, comment=comment,
                                     compatibility_code=created_item.compatibility_code,
                                     variables_name='discret_output',
                                     variables_key=choise_discret_output,
                                     exclude_variables_name='power_input',
                                     check=True, manufacturer_filter_is_required=True)

    # Блок обработки ошибки т.к. макс ток может быть не в каждом изделии
    try:
        current = created_item.variables['input_current']
    except (AttributeError, KeyError):
        current = created_item.current


    # Обрабатываем условия реверса и bypass
    if choise_reverse and choise_bypass:
        choise_nmb = choise_nmb * 3
    elif choise_bypass or choise_reverse:
        choise_nmb = choise_nmb * 2

    if created_item:
        request, created_item = add_commute_drive_item(request, category=Category_Contactor,
                                                       manufacturer=choise_manufacturer, current=current,
                                                       voltage=choise_voltage, user=user, uuid_id=uuid_id, nmb=choise_nmb,
                                                       comment=comment)

    if created_item:
        request, created_item = add_commute_drive_item(request, category=Category_CircuitBreaker,
                                                       manufacturer=choise_manufacturer, current=current,
                                                       voltage=choise_voltage, user=user, uuid_id=uuid_id, nmb=choise_nmb,
                                                       comment=comment)
    return request

# TODO: написать блок проверки по запрашиваемым полям

# функция подбора модулей для процессора согласно запрашиваемой паре входов/выходов
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
    while one_var_value > 0 or two_var_value > 0:
        watchdog += 1
        if watchdog > 100:
            break

        # создаем первую выборку изделий
        first_items = modules

        # отсортировываем выборку на наличие запрашиваемых параметров
        if one_var_value > 0:
            first_items = first_items.filter(variables__contains=one_var_name)
            first_items = first_items.order_by(
                RawSQL("Cast(variables->%s as Integer)", (one_var_name,)))

        if two_var_value > 0:
            first_items = first_items.filter(variables__contains=two_var_name)
            first_items = first_items.order_by(
                RawSQL("Cast(variables->%s as Integer)", (two_var_name,)))

        # переносим первую выборку во вторую
        second_items = first_items

        # фильтруем вторую выборку на условии меньше или равно искомому колличеству
        # сортируем выборку по искомому параметру в порядке возрастания
        if one_var_value > 0:
            second_items = second_items.filter(variables__gte={one_var_name: one_var_value})
            if not second_items.exists():
                second_items = first_items.filter(variables__lte={one_var_name: one_var_value}).reverse()

        second1_items = second_items
        if two_var_value > 0:
            second_items = second_items.filter(variables__gte={two_var_name: two_var_value})
            if not second_items.exists():
                second_items = second1_items.filter(variables__lte={two_var_name: two_var_value})

        # переносим вторую выборку в третью
        third_items = second_items

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

        # если изедий в выборке нет то возвращаемся к первой выборке
        if not items:
            items = first_items

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
                            places_list[for_index] = [place_name, place_value]

                        # если кол-во доступных мест в изделии меньше или = 0, то исключаем из выборки module (перед циклом while) все изделия (модули) с таким требуемым расположением
                        else:
                            modules = modules.exclude(variables__contains=place_name)
                            try:
                                if items_list[len(items_list) - 1][0].variables[place_name]:
                                    items_list.pop()
                            except KeyError:
                                None

                # если при получении переменной hstore с именем запрашиваемого места расположения модуля происходит ошибка ключа (ключ не найден) то ничего не делаем и пропускаем выборку
                except KeyError:
                    None

                for_index += 1
        else:
            # Если и в этом случае нет изделий, прерываем цикл и выдаем сообщение об ошибке
            messages.info(request, u'Ошибка: невозможно выполнить подбор. Уменьшите заданные критерии.')
            error = True
            break

    return request, items_list, one_var_value, two_var_value, error

# функция добавления комплектующих управления
def add_control_items_into_estimate(request):

    data = request.POST
    user = request.user

    # создаем уникальный идентификатор
    uuid_id = uuid4()

    # Выгружаем данные из посылки
    comment = str(data["pre_comment"] or None) + str(' ') + str(data["comment"] or None)

    choised_voltage = data["calc_control_voltage"] or 0
    choised_type = data["calc_control_type"] or None
    choised_manufacturer = data["calc_control_manufacturer"] or None
    choised_series = data["calc_control_series"] or None
    choised_cpu = data["calc_control_cpu"] or None

    choised_time_delay = request.POST.get('calc_control_time_delay') or 3

    choised_discret_input = request.POST.get('calc_control_discret_input') or 0
    choised_discret_output = request.POST.get('calc_control_discret_output') or 0

    choised_manufacturer_relays = data["calc_control_manufacturer_relays"] or None
    choised_series_relays = data["calc_control_series_relays"] or None

    choised_reserve = request.POST.get('calc_control_reserve') or 1
    if float(choised_reserve) < 1: choised_reserve = 1

    discret_input = round(int(choised_discret_input)*float(choised_reserve), 0)
    discret_output = round(int(choised_discret_output)*float(choised_reserve), 0)

    # буфер запрашиваемых сигналов заполняется как лист с вложенным в него словарем пары запрашиваемых сигналов
    signals = []

    # буфер подобранных изделий, где items_list[модель изделия][кол-во]
    items_list = []

    # добавляем запрашиваемые сигналы в буфер
    if discret_input or discret_output:
        signals.append({"discret_input":discret_input, "discret_output": discret_output})
    # TODO: Добавить остальные типы входов и выходов

    if settings.DEBUG:
        messages.info(request, u'Запрашиваемые сигналы: %s' % signals)

    # Запрашиваем все активные изделия из БД
    items = Item.objects.filter(is_active=True)

    # если выбрано напряжение, фильтруем запрос по выбранному напряжению
    if choised_voltage:
        items = items.filter(voltage=choised_voltage)

    # Если выбран тип управления релейная схема
    if choised_type == "Relay":
        # Получаем категории реле времени и промежуточных реле
        relay_category_name = u'Реле'

        # Запрашиваем все изделия из категорий и подкатеорий изделий
        relays = items.filter(
            category__in=ItemCategory.objects.get(name=relay_category_name).get_descendants(include_self=True))

        # если выбран производитель, фильтруем запрос по выбранному производителю
        if choised_manufacturer:
            relays = relays.filter(manufacturer__name=choised_manufacturer)

        # Если выбрана серия, фильтруем согласно серии изделий
        if choised_series:
            relays = relays.filter(series=choised_series)

        # Получаем кол-во запрошенных временных задержек
        nmb_time_delay = int(choised_time_delay)

        # Если кол-во временных задержек присутсвует в запросе от пользователя
        if nmb_time_delay:
            # Получаем изделия только с hstore полем time_delay
            time_relays = relays.filter(variables__contains='time_delay')
            # Выбираем первое изделие реле времени из запроса изделий
            time_relay = time_relays.first()

            # Если реле времени найдено
            if time_relay:

                # Получаем кол-во временных задержек
                try:
                    nmb_time_delay = round(nmb_time_delay/int(time_relay.variables['time_delay']), 0)
                except KeyError:
                    messages.info(request, u'В Базе данных нет изделия с соответсвующими критериями.')

                # Добавляем изделие в список подобранных изделий
                items_list.append([time_relay, nmb_time_delay])

    # Если выбран тип управления ПЛК или Программируемое реле
    elif choised_type == "PLC" or choised_type == "ProgrammableRelay":

        # Присваиваем категорию изделий для поиска изделий согласно выбору типа управления
        if choised_type == "PLC":
            plc_category_name = u'ПЛК'
            module_category_name = u'Модуль расширения ПЛК'
        else:
            plc_category_name = u'Реле модульное'
            module_category_name = u'Модуль расширения программируемого реле'

        # Запрашиваем все изделия из категорий и подкатеорий изделий
        cpu = items.filter(
            category__in=ItemCategory.objects.get(name=plc_category_name).get_descendants(include_self=True))

        # Оставляем только изделия с полем main_item - основное изделие
        cpu = cpu.filter(variables__contains='main_item')


        # если выбран производитель, фильтруем запрос по выбранному производителю
        if choised_manufacturer:
            cpu = cpu.filter(manufacturer__name=choised_manufacturer)

        # Если выбрана серия, фильтруем согласно серии изделий
        if choised_series:
            cpu = cpu.filter(series=choised_series)

        # Если выбран конкретный cpu то ставим именно его
        if choised_cpu:
            cpu = cpu.get(name=choised_cpu)
        # Иначе подбираем процессор
        else:
            # Если в запрашиваемых сигналах присутсвуют дискретные входа, то фильтруем запрос процессоров на большее кол-во максимальных входов
            if discret_input:
                cpu = cpu.filter(variables__gte={"max_discret_inputs": discret_input})
            # Также поступаем и с дискретными входами
            if discret_output:
                cpu = cpu.filter(variables__gte={"max_discret_outputs": discret_output})
            # TODO: К дискретным входам и выходам сложить быстрые дискртеные входы и выходы

            # Сортируем запрос процессоров по id (порядковому числу их добавления БД)
            cpu = cpu.order_by('id')
            # Оставляем первый в выборке процессор
            cpu = cpu.first()

        # Если процессор в выборке присутсвует
        if cpu:

            # Получаем от процессора максимально возможное кол-во модулей
            places_list = []

            # Слева от процессора
            try:
                places_list.append(["left_places", cpu.variables["left_places"]])
            except KeyError:None

            # Справа от процессора
            try:
                places_list.append(["right_places", cpu.variables["right_places"]])
            except KeyError:None

            # На борту процессора
            try:
                places_list.append(["board_places", cpu.variables["board_places"]])
            except KeyError:None

            # Обходим циклом пары сигналов из списка запрашиваемых сигналов
            for pair in signals:
                # Также обходим циклом, все ключи в паре, и вычитаем из конкретно запрашиваемых сигналов, сигналы которые уже присутсвуют на борту
                for key in pair.keys():
                    try:
                        pair[key] -= int(cpu.variables[key])
                    except KeyError:None

            # Добавляем процессор в список подобранных изделий
            items_list.append([cpu, 1])

            # Обходим циклом все пары сигналов из списка запрашиваемых сигналов оставшихся после добавления процессора
            for pair in signals:
                # Получаем имя и величину запрашиваемого сигнала для первоидущего и следующего подбираемого сигнала
                first_signal_name = list(pair.keys())[0]
                first_signal_value = pair[list(pair.keys())[0]]
                second_signal_name = list(pair.keys())[1]
                second_signal_value = pair[list(pair.keys())[1]]

                # Вызываем функцию подбора модулей, а в ответ получаем оставшееся кол-во запрашиваемых сигналов
                request, items_list, pair[first_signal_name], pair[second_signal_name], \
                                                            error = select_control_items(request=request, items_list=items_list,
                                                                                         one_var_name=first_signal_name,
                                                                                         one_var_value=first_signal_value,
                                                                                         compatibility_code=cpu.compatibility_code,
                                                                                         category__name=module_category_name,
                                                                                         two_var_name=second_signal_name,
                                                                                         two_var_value=second_signal_value,
                                                                                         places_list=places_list
                                                                                         )

            if settings.DEBUG:
                messages.info(request,
                              u'Осталось %s' % (signals))
                for key, value in items_list:

                    messages.info(request, u'Изделие: %s, кол-во: %s ' % (key.name, value))

            # Проверяем на недобор запрашиваемых сигналов
            for pair in signals:
                if pair[list(pair.keys())[0]] > 0:
                    messages.info(request, u'Невозможно подобрать. Осталось %s в кол-ве: %s' %
                                  (list(pair.keys())[0], pair[list(pair.keys())[0]]))
                    items_list = None
                    break
                elif pair[list(pair.keys())[1]] > 0:
                    messages.info(request, u'Невозможно подобрать. Осталось %s в кол-ве: %s' %
                                  (list(pair.keys())[1], pair[list(pair.keys())[1]]))
                    items_list = None
                    break


        else:
            messages.info(request, u'Подходящего процессора не найдено. Упростите критерии.')


    #  Функция подбора промежуточных реле
    if items_list:

        relay_category_name = u'Реле'

        # Запрашиваем все изделия из категорий и подкатеорий изделий
        discret_relays = items.filter(
            category__in=ItemCategory.objects.get(name=relay_category_name).get_descendants(include_self=True))

        # Фильтруем по производителю, если выбрано пользователем
        if choised_manufacturer_relays:
            discret_relays=discret_relays.filter(manufacturer__name=choised_manufacturer_relays)

        # Фильтруем по серии, если выбрано пользователем
        if choised_series_relays:
            discret_relays=discret_relays.filter(series=choised_series_relays)

        if discret_input:
            # Получаем изделия только с hstore полем discret_input
            discret_relays = discret_relays.filter(variables__contains='discret_input')
        if discret_output:
            # Получаем изделия только с hstore полем discret_output
            discret_relays = discret_relays.filter(variables__contains='discret_output')

        # Выбираем первое изделие промежуточного реле из запроса изделий
        discret_relay = discret_relays.first()
        # Добавляем изделие в список подобранных изделий
        if discret_relay:
            items_list.append([discret_relay, discret_input + discret_output])

    if items_list:
        for item, nmb in items_list:

            # Добавляем изделия в смету
            created, request = created_item_in_estimate(request=request, user=user, uuid_id=uuid_id,
                                                        item_id=item.id, is_active=True, nmb=nmb,
                                                        comment=comment,
                                                        input_query={'choised_type': choised_type,
                                                                     'compatibility_code': str(item.compatibility_code),
                                                                     'category_id': str(item.category_id)})

            # Если добавлено успешно, добавляем обязательные изделия добавленного изделия
            if created:
                for adding_item in Item.objects.filter(id=created.item_id).values(
                        'main_item__adding_item', 'main_item__nmb'):
                    if adding_item.get('main_item__adding_item'):
                        created_item_in_estimate(request=request, user=user, uuid_id=uuid_id,
                                                 item_id=adding_item.get('main_item__adding_item'),
                                                 is_active=True,
                                                 nmb=adding_item.get('main_item__nmb') * nmb,
                                                 comment=comment)
    else:
        messages.info(request, u'Изделия подобрать невозможно. Упростите критерии.')

    return request