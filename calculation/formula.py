# -*- coding: utf-8 -*-
from .models import ItemInEstimate
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from uuid import uuid4
from database_item.models import ItemCategory, Item
from decimal import Decimal

# функция добавления изделия в смету или выдачи ошибки
def created_item_in_estimate(request, user,  uuid_id, item_id, is_active, nmb, comment):
    created = ItemInEstimate.objects.create(uuid_id=uuid_id, user=user, item_id=item_id,
                                            is_active=is_active, nmb=nmb, comment=comment)
    if created:
        messages.success(request, u'Изделие %s успешно добавлено' % (str(item_id)))
        return request
    else:
        messages.error(request, u'Невозможно добавить изделие в смету. Обратитесь в тех.поддержку')
        return request

# функция удаления из сметы всех изделий по совпадению uuid
def delete_uuid_id_in_estimate(request, user, uuid_id):
    delete_items = ItemInEstimate.objects.filter(uuid_id=uuid_id, user=user)
    delete_items.delete()
    messages.warning(request, 'Выбранные изделия из сметы удалены.')
    return request

def add_commute_drive_item(request, category, manufacturer, current, voltage, user, uuid_id, nmb, comment):

    if manufacturer == None or manufacturer == '':
        item = Item.objects.filter(category=category, current__gte=current, voltage__gte=voltage,
                                   is_active=True).first()
    else:
        item = Item.objects.filter(category=category, manufacturer__name=manufacturer, power__gte=power,
                               voltage__gte=voltage,
                               is_active=True).first()

    if item:
        # добавляем устройство в смету
        request = created_item_in_estimate(request=request, user=user, uuid_id=uuid_id,
                                                         item_id=item.id, is_active=True, nmb=nmb, comment=comment)
    else:
        request = delete_uuid_id_in_estimate(request=request, user=user, uuid_id=uuid_id)
        messages.info(request, u'Изделие не найдено.')

    return request


# функция добавления изделий коммутации привода в смету
def add_commute_drive_items_into_estimate(user, request):
    data = request.POST

    # создаем уникальный идентификатор
    uuid_id = uuid4()

    # Выгружаем данные из посылки
    comment = u'Привод '+data["comment"]
    voltage = data["voltage"]
    power = data["power"]
    type = data["type"]
    atributes = data.get('atributes') or None
    manufacturer = data.get('manufacturer') or None
    manufacturer_terminals = data.get('manufacturer_terminals') or None
    choise_reverse = data.get('choise_reverse', False)
    choise_bypass = data.get('choise_bypass', False)

    # формула расчета тока по мощности и напряжению для подбора коммутации привода
    current =((Decimal(power) * Decimal(1000)) / (Decimal(voltage) * Decimal('0.8')))

    # получаем категории из списка категорий
    Category_Disconnector = ItemCategory.objects.filter(name__startswith='Рубильник').first()
    Category_CircuitBreaker = ItemCategory.objects.filter(name__startswith='Автоматический выключатель').first()
    Category_Contactor = ItemCategory.objects.filter(name__startswith='Контактор').first()
    Category_FreqConverter = ItemCategory.objects.filter(name__startswith='Устройство плавного пуска').first()
    Category_SoftStarter = ItemCategory.objects.filter(name__startswith='Частотный преобразователь').first()

    request = add_commute_drive_item(request, category=Category_Disconnector, manufacturer=manufacturer, current=current,
                       voltage=voltage, user=user, uuid_id=uuid_id, nmb=1, comment=comment)
    request = add_commute_drive_item(request, category=Category_CircuitBreaker, manufacturer=manufacturer, current=current,
                       voltage=voltage, user=user, uuid_id=uuid_id, nmb=1, comment=comment)
    if type == 'Streight':
        request = add_commute_drive_item(request, category=Category_Contactor, manufacturer=manufacturer, current=current,
                           voltage=voltage, user=user, uuid_id=uuid_id, nmb=1, comment=comment)
    elif type == 'SoftStart':
        request = add_commute_drive_item(request, category=Category_Contactor, manufacturer=manufacturer, current=current,
                           voltage=voltage, user=user, uuid_id=uuid_id, nmb=1, comment=comment)
        request = add_commute_drive_item(request, category=Category_SoftStarter, manufacturer=manufacturer, current=current,
                           voltage=voltage, user=user, uuid_id=uuid_id, nmb=1, comment=comment)
    elif type == 'FreqConvert':
        request = add_commute_drive_item(request, category=Category_Contactor, manufacturer=manufacturer, current=current,
                           voltage=voltage, user=user, uuid_id=uuid_id, nmb=1, comment=comment)
        request = add_commute_drive_item(request, category=Category_FreqConverter, manufacturer=manufacturer, current=current,
                           voltage=voltage, user=user, uuid_id=uuid_id, nmb=1, comment=comment)

    # TODO: Убрать лишние поля в БД и настроить логику на поиск и добавление по атрибутам
    # TODO: Настроить импорт экспорт данных полей
    # temp = Item.objects.filter(atributes__contains='a').first()
    # print(temp.id)
    # temp = Item.objects.get(id=temp.id).atributes['a']
    # print(temp)
    return locals()