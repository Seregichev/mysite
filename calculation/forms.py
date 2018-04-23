from django import forms
from database_item.models import Item, ItemManufacturer, ItemCategory


class CalcForm (forms.Form):
    comment = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': u'Назначение', 'class': 'form-control'}),
                              )


class CalcNmb (forms.Form):
    calc_nmb = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'pattern': '^[ 1-9]+$'}),
                                  required=True, initial=1)


class CalcDriveForm (forms.Form):

    CHOISES_VOLTAGE = (
        ('380', '380 ~'),
        ('690', '690 ~'),
    )

    CHOISES_POWER = (
        (None, '-----'),
        ('0.75', '0,75'), ('1.5', '1,5'), ('2.2', '2,2'), ('3', '3'), ('4', '4'), ('5.5', '5,5'), ('7.5', '7,5'),
        ('11', '11'), ('15', '15'), ('18.5', '18,5'), ('22', '22'), ('30', '30'), ('37', '37'),
        ('45', '45'), ('55', '55'), ('75', '75'), ('90', '90'), ('110', '110'), ('132', '132'),
        ('160', '160'), ('200', '200'), ('220', '220'), ('250', '250'), ('280', '280'), ('315', '315'),
        ('355', '355'), ('400', '400'), ('500', '500')
    )

    TYPE_COMMUTATION = (
        ('Streight', u'Прямой пуск'),
        ('SoftStart', u'Устройство плавного пуска'),
        ('FreqConvert', u'Частотный преобразователь'),
    )

    TYPE_TERMINALS = (
        (None, '-----'),
        ('Screw', u'Винтовые'),
        ('Spring', u'Пружинные'),
        ('PushIn', u'Push-In'),
    )

    calc_drive = forms.IntegerField(widget=forms.HiddenInput(), initial='1')

    calc_drive_voltage=forms.ChoiceField(choices=CHOISES_VOLTAGE, widget=forms.Select(attrs={'class': 'form-control'}),)

    calc_drive_power = forms.ChoiceField(choices=CHOISES_POWER, widget=forms.Select(attrs={'class': 'form-control'}),)

    calc_drive_type = forms.ChoiceField(choices=TYPE_COMMUTATION, widget=forms.Select(attrs={'class': 'form-control'}),)

    # Получаем всех производителей из родительской категории
    calc_drive_manufacturer = forms.ModelChoiceField(queryset=ItemManufacturer.objects\
                                                     .filter(item__category__in=ItemCategory.objects.get(name=u'Силовая коммутация')\
                                                             .get_descendants(include_self=True))\
                                                     .values_list('name', flat=True)\
                                                     .distinct(),
                                          required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'})
                                          )

    calc_drive_series = forms.ModelChoiceField(queryset=Item.objects\
                                               .filter(category__in=ItemCategory.objects.get(name=u'Силовая коммутация')
                                                       .get_descendants(include_self=True))
                                               .values_list('series', flat=True).distinct(),
                                         required=False,
                                         widget=forms.Select(attrs={'class': 'form-control'})
                                         )

    calc_drive_reverse = forms.BooleanField(widget=forms.CheckboxInput(), label=u'Реверс', required=False)
    calc_drive_bypass = forms.BooleanField(widget=forms.CheckboxInput(), label='Bypass', required=False)

    calc_drive_discret_input = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                  'pattern': '^[ 0-9]+$'}),
                                                  label=u'Дискретные входы',
                                                  required=False)
    calc_drive_discret_output = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                  'pattern': '^[ 0-9]+$'}),
                                                  label=u'Дискретные выходы',
                                                  required=False)
    calc_drive_analog_input = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                  'pattern': '^[ 0-9]+$'}),
                                                  label=u'Аналоговые входы',
                                                  required=False)
    calc_drive_analog_output = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                  'pattern': '^[ 0-9]+$'}),
                                                  label=u'Аналоговые выходы',
                                                  required=False)
    calc_drive_profinet = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                  'pattern': '^[ 0-9]+$'}),
                                                  label=u'ProfiNet',
                                                  required=False)
    calc_drive_profibus = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                  'pattern': '^[ 0-9]+$'}),
                                                  label=u'ProfiBus',
                                                  required=False)
    calc_drive_rs485 = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                  'pattern': '^[ 0-9]+$'}),
                                             label=u'RS485',
                                             required=False)

    calc_drive_manufacturer_terminals = forms.ModelChoiceField(queryset=ItemManufacturer.objects\
                                                     .filter(item__category__in=ItemCategory.objects.get(name=u'Клеммы')\
                                                             .get_descendants(include_self=True))\
                                                     .values_list('name', flat=True)\
                                                     .distinct(),
                                            required=False,
                                            widget=forms.Select(attrs={'class': 'form-control'})
                                            )
    calc_drive_type_terminals = forms.ChoiceField(choices=TYPE_TERMINALS,
                                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                                  required=False,
                                                  )

class CalcControlForm (forms.Form):

    CHOISES_VOLTAGE = (
        ('24', '24 ⎓'),
        ('220', '220 ~'),
    )

    TYPE_CONTROL = (
        (None, '-----'),
        ('PLC', u'ПЛК'),
        ('ProgrammableRelay', u'Программируемое реле'),
        ('Relay', u'Релейная схема'),
    )

    TYPE_TERMINALS = (
        (None, '-----'),
        ('Screw', u'Винтовые'),
        ('Spring', u'Пружинные'),
        ('PushIn', u'Push-In'),
    )

    CHOISES_RESERVE = (
        ('1', '0 %'), ('1.1', '10 %'), ('1.2', '20 %'), ('1.3', '30 %'), ('1.4', '40 %'), ('1.5', '50 %'),
        ('1.6', '60 %'), ('1.7', '70 %'), ('1.8', '80 %'), ('1.9', '90 %'), ('2', '100 %')
    )

    calc_control = forms.IntegerField(widget=forms.HiddenInput(), initial='1')

    calc_control_voltage = forms.ChoiceField(choices=CHOISES_VOLTAGE,
                                           widget=forms.Select(attrs={'class': 'form-control'}), )

    calc_control_type = forms.ChoiceField(choices=TYPE_CONTROL,
                                        widget=forms.Select(attrs={'class': 'form-control'}), )

    calc_control_discret_input = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                  'pattern': '^[ 0-9]+$'}),
                                                  label=u'Дискретные входы',
                                                  required=True)
    calc_control_discret_output = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                   'pattern': '^[ 0-9]+$'}),
                                                   label=u'Дискретные выходы',
                                                   required=True)

    # Получаем всех производителей из родительской категории
    calc_control_manufacturer = forms.ModelChoiceField(queryset=ItemManufacturer.objects\
                                                     .filter(item__category__in=ItemCategory.objects.get(name=u'Управление')\
                                                     .get_descendants(include_self=True))\
                                                     .values_list('name', flat=True)\
                                                     .distinct(),
                                                     required=False,
                                                     widget=forms.Select(attrs={'class': 'form-control'})
                                                     )

    calc_control_series = forms.ModelChoiceField(queryset=Item.objects\
                                               .filter(category__in=ItemCategory.objects.get(name=u'Управление')
                                               .get_descendants(include_self=True))\
                                               .values_list('series', flat=True).distinct(),
                                               required=False,
                                               widget=forms.Select(attrs={'class': 'form-control'})
                                               )

    calc_control_cpu = forms.ModelChoiceField(queryset=Item.objects \
                                                 .filter(category__in=ItemCategory.objects.get(name=u'Управление')
                                                         .get_descendants(include_self=True),
                                                         variables__contains=['cpu'] ) \
                                                 .values_list('name', flat=True).distinct(),
                                                 required=False,
                                                 widget=forms.Select(attrs={'class': 'form-control'})
                                                 )

    calc_control_fast_discret_input = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                    'pattern': '^[ 0-9]+$'}),
                                                                                    label=u'Быстрые дискретные входы',
                                                                                    required=False)

    calc_control_fast_discret_output = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                         'pattern': '^[ 0-9]+$'}),
                                                                                     label=u'Быстрые дискретные входы',
                                                                                     required=False)

    calc_control_analog_0_10V_input = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                 'pattern': '^[ 0-9]+$'}),
                                                                                 label=u'Аналоговые 0-10V входы',
                                                                                 required=False)
    calc_control_analog_0_10V_output = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                  'pattern': '^[ 0-9]+$'}),
                                                                                  label=u'Аналоговые 0-10V выходы',
                                                                                  required=False)

    calc_control_analog_0_20mA_input = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                   'pattern': '^[ 0-9]+$'}),
                                                                                   label=u'Аналоговые 0(4)-20mA входы',
                                                                                   required=False)
    calc_control_analog_0_20mA_output = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                    'pattern': '^[ 0-9]+$'}),
                                                                                    label=u'Аналоговые 0(4)-20mA выходы',
                                                                                    required=False)

    calc_control_analog_rtd_input = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                    'pattern': '^[ 0-9]+$'}),
                                                                                    label=u'RTD входы',
                                                                                    required=False)

    calc_control_profinet = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                             'pattern': '^[ 0-9]+$'}),
                                                                             label=u'ProfiNet',
                                                                             required=False)

    calc_control_profibus = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                             'pattern': '^[ 0-9]+$'}),
                                                                             label=u'PofiBus',
                                                                             required=False)

    calc_control_modbus_tcp = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                            'pattern': '^[ 0-9]+$'}),
                                                                            label=u'Modbus TCP',
                                                                            required=False)

    calc_control_modbus_rtu = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                          'pattern': '^[ 0-9]+$'}),
                                                                          label=u'Modbus RTU',
                                                                          required=False)

    calc_control_manufacturer_relays = forms.ModelChoiceField(queryset=ItemManufacturer.objects \
                                                                 .filter(item__category__in=ItemCategory.objects \
                                                                         .get(name=u'Промежуточное реле') \
                                                                         .get_descendants(include_self=True)) \
                                                                 .values_list('name', flat=True) \
                                                                 .distinct(),
                                                                 required=False,
                                                                 widget=forms.Select(attrs={'class': 'form-control'})
                                                                 )

    calc_control_series_relays = forms.ModelChoiceField(queryset=Item.objects \
                                               .filter(category__in=ItemCategory.objects.get(name=u'Промежуточное реле') \
                                                    .get_descendants(include_self=True)) \
                                               .values_list('series', flat=True).distinct(),
                                               required=False,
                                               widget=forms.Select(attrs={'class': 'form-control'})
                                               )


    calc_control_manufacturer_terminals = forms.ModelChoiceField(queryset=ItemManufacturer.objects\
                                               .filter( item__category__in=ItemCategory.objects.get(name=u'Клеммы')\
                                                    .get_descendants(include_self=True))\
                                               .values_list('name', flat=True)\
                                               .distinct(),
                                           required=False,
                                           widget=forms.Select(attrs={'class': 'form-control'})
                                           )
    calc_control_type_terminals = forms.ChoiceField(choices=TYPE_TERMINALS,
                                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                                  required=False,
                                                  )

    calc_control_reserve = forms.ChoiceField(choices=CHOISES_RESERVE,
                                          widget=forms.Select(attrs={'class': 'form-control'}),
                                             initial=1.2)