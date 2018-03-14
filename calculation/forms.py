from django import forms
from database_item.models import Item, ItemManufacturer


class CalcForm (forms.Form):
    comment = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': u'Назначение', 'class': 'form-control'}),
                              )


class CalcDriveForm (forms.Form):

    CHOISES_VOLTAGE = (
        (None, '-----'),
        ('220', '220 ~'),
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
        (None, '-----'),
        ('Streight', u'Прямой пуск'),
        ('SoftStart', u'Устройство плавного пуска'),
        ('FreqConvert', u'Частотный преобразователь'),
    )

    TYPE_ATTRIBUTES = (
        ('reverse', u'Реверс'),
        ('bypass', 'Bypass'),
        ('discret_input', u'Дискретный входы'),
        ('discret_output', u'Дискретные выходы'),
        ('analog_input', u'Аналоговые входы'),
        ('analog_output', u'Аналоговые выходы'),
        ('profinet', 'ProfiNet'),
        ('profibus', 'PofiBus'),
        ('rs485', 'RS485'),
    )

    calc_drive = forms.IntegerField(widget=forms.HiddenInput(), initial='1')

    voltage=forms.ChoiceField(choices=CHOISES_VOLTAGE, widget=forms.Select(attrs={'class': 'form-control'}),)

    power = forms.ChoiceField(choices=CHOISES_POWER, widget=forms.Select(attrs={'class': 'form-control'}),)

    type = forms.ChoiceField(choices=TYPE_COMMUTATION, widget=forms.Select(attrs={'class': 'form-control'}),)

    manufacturer = forms.ModelChoiceField(queryset=ItemManufacturer.objects.all()\
                                          .values_list('name', flat=True).distinct(),
                                          required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'})
                                          )
    attributes = forms.MultipleChoiceField(choices=TYPE_ATTRIBUTES,
                                          widget=forms.CheckboxSelectMultiple(),
                                          initial={
                                              'discret_input': 1, 'discret_output': 1,
                                              'analog_input': 1, 'analog_output': 1,
                                          }
                                  )


    manufacturer_terminals = forms.ModelChoiceField(queryset=ItemManufacturer.objects.all()\
                                            .values_list('name', flat=True).distinct(),
                                            required=False,
                                            widget=forms.Select(attrs={'class': 'form-control'})
                                            )

# class AddControlForm(forms.Form):
#
#     # обозначаем в параметре inital как форма добавления изделий комутации электродвигателя
#     appointment = forms.IntegerField(widget=forms.HiddenInput(), initial='add_control_items')
#
#     comment = forms.CharField(required=True, widget=forms.TextInput(
#                                 attrs={'placeholder': u'Назначение', 'class': 'form-control'}),
#                                 error_messages={'required': 'Пожалуйста укажите назначение'},
#                                 )
#
#     type = forms.ModelChoiceField(queryset=Parameter.objects.filter(
#                                     category=CategoryParameter.objects.filter(name=u'Тип управления', is_active=True),
#                                     is_active=True),
#                                     error_messages={'required': 'Пожалуйста выберите тип управления'},
#                                     widget=forms.Select(attrs={'class': 'form-control'})
#     )
#
#     manufacturer = forms.ModelChoiceField(queryset=Parameter.objects.filter(
#         category=CategoryParameter.objects.filter(name=u'Тип управления', is_active=True),
#         itemcategoryparameter__main_category=True)\
#                                           .values_list('itemcategoryparameter__item_category__item__manufacturer__name',
#                                            flat=True).distinct(), widget=forms.Select(attrs={'class': 'form-control'})
#                                           )
#
#     series = forms.ModelChoiceField(queryset=Parameter.objects.filter(
#         category=CategoryParameter.objects.filter(name=u'Тип управления', is_active=True),
#         itemcategoryparameter__main_category=True)\
#                                         .values_list('itemcategoryparameter__item_category__item__series',
#                                                        flat=True).distinct(),
#                                         widget=forms.Select(attrs={'class': 'form-control'})
#                                         )
#
#     discret_inputs = forms.IntegerField(required=True,
#                                         error_messages={'required': 'Пожалуйста выберите кол-во дискретных входов'},
#                                         widget=forms.NumberInput(attrs={'class': 'form-control'})
#                                         )
#
#     discret_outputs = forms.IntegerField(required=True,
#                                        error_messages={'required': 'Пожалуйста выберите кол-во дискретных выходов'},
#                                        widget=forms.NumberInput(attrs={'class': 'form-control'})
#                                        )
#
#     analog_inputs = forms.IntegerField(required=False,
#                                        error_messages={'required': 'Пожалуйста выберите кол-во аналоговых входов'},
#                                        widget=forms.NumberInput(attrs={'class': 'form-control'})
#                                        )
#
#     analog_outputs = forms.IntegerField(required=False,
#                                         error_messages={'required': 'Пожалуйста выберите кол-во аналоговых выходов'},
#                                         widget=forms.NumberInput(attrs={'class': 'form-control'})
#                                         )
#
#     temperature_inputs = forms.IntegerField(required=False,
#                                        error_messages={'required': 'Пожалуйста выберите кол-во температурных входов'},
#                                        widget=forms.NumberInput(attrs={'class': 'form-control'})
#                                        )
#
#     atributes = forms.ModelChoiceField(queryset=Parameter.objects.filter(
#         category=CategoryParameter.objects.filter(name=u'Тип управления', is_active=True))\
#                                        .values_list('itemcategoryparameter__item_category__item__atributes__name',
#                                                     flat=True).distinct(),
#                                        required=False,
#                                        widget=forms.Select(attrs={'class': 'form-control'})
#                                        )
#
#     manufacturer_relays = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True,
#                                                     category=int(category_relays))\
#                                                     .values_list('manufacturer__name', flat=True).distinct(),
#                                                     required=False,
#                                                     widget=forms.Select(attrs={'class': 'form-control'})
#                                                     )
#
#     manufacturer_terminals = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True,
#                                             category=int(category_terminals))\
#                                             .values_list('manufacturer__name', flat=True).distinct(),
#                                             required=False,
#                                             widget=forms.Select(attrs={'class': 'form-control'})
#                                             )
#
#
