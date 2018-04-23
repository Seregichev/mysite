# -*- coding: utf-8 -*-
from django.views.generic import ListView
from .models import Calculate, ItemInEstimate, ItemInCalculate
from database_item.models import Item, ItemCategory
from .formula import delete_uuid_id_in_estimate
from django.http import JsonResponse
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum

class CalculateList(ListView):
    template_name = "apps/calculate.html"

    context_object_name = 'calculates'

    def get_queryset(self):
        return Calculate.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(CalculateList, self).get_context_data(**kwargs)
        context['item_in_calculate'] = ItemInCalculate.objects.filter(calculate__user=self.request.user)
        return context

class EstimateList(ListView):
    template_name = "apps/estimate.html"

    context_object_name = 'estimate'

    def get_queryset(self):
        return ItemInEstimate.objects.filter(user=self.request.user).order_by('updated','uuid_id')

    def get_context_data(self, **kwargs):
        context = super(EstimateList, self).get_context_data(**kwargs)
        context['estimate_price'] = ItemInEstimate.objects.filter(user=self.request.user).aggregate(sum=Sum('total_price'))
        return context

    # функция удаления из сметы изделий по uuid
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            data = request.POST
            user = request.user
            if data["appointment"] == 'delete_items':
                request = delete_uuid_id_in_estimate(request=request, user=user, uuid_id=data["uuid_id"])
        return self.get(request, *args, **kwargs)


def check_calc_drive_fields(request):
    return_dict = dict()

    if settings.DEBUG:
        print(u'Запрос AJAX для привода пришел:')
        print(request.POST)

    if request.POST:

        # Получаем переменные из запроса
        data = request.POST

        choise_voltage = data["calc_drive_voltage"] or None
        choise_power = data["calc_drive_power"] or None
        choise_type = data["calc_drive_type"] or None
        choise_manufacturer = data.get('calc_drive_manufacturer') or None
        choise_series = data.get('calc_drive_series') or None
        choise_terminal_manufacturer = data.get('calc_drive_manufacturer_terminals') or None
        choise_type_terminals = data.get('calc_drive_type_terminals') or None

        choise_discret_input = data.get('calc_drive_discret_input') or None
        choise_discret_output = data.get('calc_drive_discret_output') or None
        choise_analog_input = data.get('calc_drive_analog_input') or None
        choise_analog_output = data.get('calc_drive_analog_output') or None
        choise_profinet = data.get('calc_drive_profinet') or None
        choise_profibus = data.get('calc_drive_profibus') or None
        choise_rs485 = data.get('calc_drive_rs485') or None

        # формула расчета тока по мощности и напряжению для подбора коммутации привода
        current = ((Decimal(choise_power) * Decimal(1000)) / (Decimal(choise_voltage) * Decimal(settings.COSINE_PHI)))

        items = Item.objects.filter(is_active=True)

        terminal_manufacturers = items.filter(category__in=ItemCategory.objects.get(name=u'Клеммы')\
                                                            .get_descendants(include_self=True))\
                                                            .values_list('manufacturer__name', flat=True)\
                                                            .distinct()

        other_power_items = items.filter(current__gte=current, voltage__gte=choise_voltage)

        if choise_type == 'Streight':
            category_termrele = ItemCategory.objects.filter(name__startswith='Тепловое реле').first()
            items = items.filter(category__in=ItemCategory.objects.get(id=category_termrele.id).get_descendants(include_self=True))

        if choise_type == 'SoftStart':
            category_softstarter = ItemCategory.objects.filter(name__startswith='Устройство плавного пуска').first()
            items = items.filter(category__in=ItemCategory.objects.get(id=category_softstarter.id).get_descendants(include_self=True))

        if choise_type == 'FreqConvert':
            category_freqconverter = ItemCategory.objects.filter(name__startswith='Частотный преобразователь').first()
            items = items.filter(category__in=ItemCategory.objects.get(id=category_freqconverter.id).get_descendants(include_self=True))


        power_items = items.filter(current__gte=current, voltage__gte=choise_voltage)


        manufacturers = power_items.values_list('manufacturer__name').distinct()

        if choise_manufacturer:
            items = items.filter(manufacturer__name=choise_manufacturer)
            power_items = power_items.filter(manufacturer__name=choise_manufacturer)

        series = power_items.values_list('series').distinct()

        if choise_series:
            items = items.filter(series=choise_series)
            power_items = power_items.filter(series=choise_series)

        discret_input = items.filter(variables__gte={'discret_input': 1}).exists()

        if choise_discret_input:
            items = items.filter(variables__gte={'discret_input': int(choise_discret_input)})

        discret_output = items.filter(variables__gte={'discret_output': 1}).exists()

        if choise_discret_output:
            items = items.filter(variables__gte={'discret_output': int(choise_discret_output)})

        analog_input = items.filter(variables__gte={'analog_input': 1}).exists()

        if choise_analog_input:
            items = items.filter(variables__gte={'analog_input': int(choise_analog_input)})

        analog_output = items.filter(variables__gte={'analog_output': 1}).exists()

        if choise_analog_output:
            items = items.filter(variables__gte={'analog_output': int(choise_analog_output)})

        profinet = items.filter(variables__gte={'profinet': 1}).exists()

        if choise_profinet:
            items = items.filter(variables__gte={'profinet': int(choise_profinet)})

        profibus = items.filter(variables__gte={'profibus': 1}).exists()

        if choise_profibus:
            items = items.filter(variables__gte={'profibus': int(choise_profibus)})

        rs485 = items.filter(variables__gte={'rs485': 1}).exists()

        if choise_rs485:
            items = items.filter(variables__gte={'rs485': int(choise_rs485)})

        # 1-ая проверка на наличие изделий по фильтрам и основных силовых сизделий
        if items.exists() and power_items.exists():
            general_checking = True
        else:
            general_checking = False

        # 2-ая проверка на наличие остальных силовых изделий соглсано фильтру напряжения и тока
        if general_checking:
            general_checking = False

            Category_CircuitBreaker = ItemCategory.objects.filter(name__startswith='Автоматический выключатель').first()
            Category_Contactor = ItemCategory.objects.filter(name__startswith='Контактор').first()

            circuitbreakers = other_power_items.filter(
                category__in=ItemCategory.objects.get(id=Category_CircuitBreaker.id).get_descendants(include_self=True))
            contactor = other_power_items.filter(
                category__in=ItemCategory.objects.get(id=Category_Contactor.id).get_descendants(include_self=True))

            if circuitbreakers.exists() and contactor.exists():
                general_checking = True

        # if general_checking:
        #     general_checking = terminal_manufacturers.exists()
        #
        #     if choise_terminal_manufacturer:
        #         general_checking = terminal_manufacturers.filter(category__name=choise_terminal_manufacturer).exists()
        #
        #     if choise_type_terminals:
        #         general_checking = terminal_manufacturers.filter(variables__icontains=choise_type_terminals).exists()
        # TODO: Расскоментировать когда добавяться клеммы

        # выдача возвращаемого словаря
        return_dict["manufacturers"] = list()
        for manufacturer in manufacturers:
            return_dict['manufacturers'].append(manufacturer)

        return_dict["series"] = list()
        for one in series:
            return_dict['series'].append(one)

        return_dict['discret_input'] = discret_input
        return_dict['discret_output'] = discret_output
        return_dict['analog_input'] = analog_input
        return_dict['analog_output'] = analog_output
        return_dict['profinet'] = profinet
        return_dict['profibus'] = profibus
        return_dict['rs485'] = rs485

        return_dict["terminal_manufacturers"] = list()
        for terminal_manufacturer in terminal_manufacturers:
            return_dict['terminal_manufacturers'].append(terminal_manufacturer)

        return_dict['general_checking'] = general_checking

    return JsonResponse(return_dict)

def check_calc_control_fields(request):
    return_dict = dict()

    if settings.DEBUG:
        print(u'Запрос AJAX для управления пришел:')
        print(request.POST)

    if request.POST:

        # Получаем переменные из запроса
        data = request.POST

        choise_voltage = data["calc_control_voltage"] or None
        choise_type = data["calc_control_type"] or None
        choise_manufacturer = data.get('calc_control_manufacturer') or None
        choise_series = data.get('calc_control_series') or None
        choise_cpu = data.get('calc_control_cpu') or None
        choise_relays_manufacturer = data.get('calc_control_manufacturer_relays') or None
        choise_relays_series = data.get('calc_control_series_relays') or None
        choise_terminal_manufacturer = data.get('calc_drive_manufacturer_terminals') or None
        choise_type_terminals = data.get('calc_drive_type_terminals') or None

        choise_discret_input = data.get('calc_control_discret_input') or None
        choise_discret_output = data.get('calc_control_discret_output') or None
        choise_fast_discret_input = data.get('calc_control_fast_discret_input') or None
        choise_fast_discret_output = data.get('calc_control_fast_discret_output') or None
        choise_analog_0_10V_input = data.get('calc_control_analog_0_10V_input') or None
        choise_analog_0_10V_output = data.get('calc_control_analog_0_10V_output') or None
        choise_analog_0_20mA_input = data.get('calc_control_analog_0_20mA_input') or None
        choise_analog_0_20mA_output = data.get('calc_control_analog_0_20mA_output') or None
        choise_analog_rtd_input = data.get('calc_control_analog_rtd_inpu') or None
        choise_profinet = data.get('calc_control_profinet') or None
        choise_profibus = data.get('calc_control_profibus') or None
        choise_modbus_tcp = data.get('calc_control_modbus_tcp') or None
        choise_modbus_rtu = data.get('calc_control_modbus_rtu') or None

        print(data)

        category = None

        items = Item.objects.filter(is_active=True)

        if choise_voltage:
            items = items.filter(voltage=choise_voltage)

        terminal_manufacturers = items.filter(category__in=ItemCategory.objects.get(name=u'Клеммы') \
                                              .get_descendants(include_self=True)) \
                                                .values_list('manufacturer__name', flat=True) \
                                                .distinct()

        if choise_type == 'Relay':
            category = ItemCategory.objects.filter(name__startswith=u'Реле').first()

        if choise_type == 'ProgrammableRelay':
            category = ItemCategory.objects.filter(name__startswith=u'Программируемое реле').first()

        if choise_type == 'PLC':
            category = ItemCategory.objects.filter(name__startswith=u'ПЛК').first()

        if category:
            items = items.filter(category__in=ItemCategory.objects.get(id=category.id).get_descendants(include_self=True))

        main_items = items.filter(variables__contains='main_item')

        manufacturers = main_items.values_list('manufacturer__name').distinct()

        if choise_manufacturer:
            main_items = main_items.filter(manufacturer__name=choise_manufacturer)

        series = main_items.values_list('series').distinct()

        if choise_series:
            main_items = main_items.filter(series=choise_series)

        cpu = main_items.values_list('name').distinct()

        if choise_cpu:
            main_items = main_items.filter(series=choise_series)

        adding_items = items

        if main_items:
            adding_items = adding_items.filter(compatibility_code=main_items.first().compatibility_code)

        discret_input = adding_items.filter(variables__contains='discret_input').exists()

        discret_output = adding_items.filter(variables__contains='discret_output').exists()

        fast_discret_input = adding_items.filter(variables__contains='fast_discret_input').exists()

        fast_discret_output = adding_items.filter(variables__contains='fast_discret_output').exists()

        analog_0_10V_input = adding_items.filter(variables__contains='analog_0_10V_input').exists()

        analog_0_10V_output = adding_items.filter(variables__contains='analog_0_10V_output').exists()

        analog_0_20mA_input = adding_items.filter(variables__contains='analog_0_20mA_input').exists()

        analog_0_20mA_output = adding_items.filter(variables__contains='analog_0_20mA_output').exists()

        analog_rtd_input = adding_items.filter(variables__contains='analog_rtd_input').exists()

        profinet = adding_items.filter(variables__contains='profinet').exists()

        profibus = adding_items.filter(variables__contains='profibus').exists()

        modbus_tcp = adding_items.filter(variables__contains='modbus_tcp').exists()

        modbus_rtu = adding_items.filter(variables__contains='modbus_rtu').exists()

        # выдача возвращаемого словаря
        return_dict["manufacturers"] = list()
        for manufacturer in manufacturers:
            return_dict['manufacturers'].append(manufacturer)

        return_dict["series"] = list()
        for one in series:
            return_dict['series'].append(one)

        return_dict["cpu"] = list()
        for one in cpu:
            return_dict['cpu'].append(one)

        return_dict['discret_input'] = discret_input
        return_dict['discret_output'] = discret_output
        return_dict['fast_discret_input'] = fast_discret_input
        return_dict['fast_discret_output'] = fast_discret_output
        return_dict['analog_0_10V_input'] = analog_0_10V_input
        return_dict['analog_0_10V_output'] = analog_0_10V_output
        return_dict['analog_0_20mA_input'] = analog_0_20mA_input
        return_dict['analog_0_20mA_output'] = analog_0_20mA_output
        return_dict['analog_rtd_input'] = analog_rtd_input
        return_dict['profinet'] = profinet
        return_dict['profibus'] = profibus
        return_dict['modbus_tcp'] = modbus_tcp
        return_dict['modbus_rtu'] = modbus_rtu

        return_dict["terminal_manufacturers"] = list()
        for terminal_manufacturer in terminal_manufacturers:
            return_dict['terminal_manufacturers'].append(terminal_manufacturer)

        if main_items:
            return_dict['general_checking'] = True

    return JsonResponse(return_dict)

# TODO: Добавить обработку выпадающих списков промежуточных реле