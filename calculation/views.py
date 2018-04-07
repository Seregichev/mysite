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


def check_fields_in_calculator(request):
    return_dict = dict()

    if settings.DEBUG:
        print(u'Запрос AJAX пришел:')
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
