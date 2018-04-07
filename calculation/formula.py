# -*- coding: utf-8 -*-
from .models import ItemInEstimate
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from uuid import uuid4
from database_item.models import ItemCategory, Item
from decimal import Decimal
from django.conf import settings


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
