from django import forms
from database_item.models import Item, ItemManufacturer

class CalcForm (forms.Form):
    comment = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': u'Назначение', 'class': 'form-control'}),
                              )

class CalcDriveForm (forms.Form):

    TYPE_COMMUTATION = (
        ('Streight', u'Прямой пуск'),
        ('SoftStart', u'Устройство плавного пуска'),
        ('FreqConvert', u'Частотный преобразователь'),
    )

    TYPE_COMMUNICATION = (
        ('Discret', u'Дискретный'),
        ('Analog', u'Аналоговый'),
        ('Profinet', u'ProfiNet'),
        ('Profibus', u'PofiBus'),
        ('Ethernet', u'EtherNet'),
        ('RS485', u'RS485'),
        ('RS485', u'RS232'),
    )

    calc_drive = forms.IntegerField(widget=forms.HiddenInput(), initial='1')


    voltage = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True).values_list('voltage', flat=True)\
                                    .order_by('voltage').distinct(),
                                     widget=forms.Select(attrs={'class': 'form-control'})
                                     )

    power = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True).values_list('power', flat=True)\
                                   .order_by('power').distinct(),
                                   widget=forms.Select(attrs={'class': 'form-control'})
                                   )

    type = forms.ChoiceField(choices=TYPE_COMMUTATION, widget = forms.Select(attrs={'class': 'form-control'}),
                                  )

    choise_reverse = forms.BooleanField(label='Функция Реверс',
                                        help_text=u'Добавляет в схему дополнительные изделия для запуска двигателя в обратную сторону',
                                        required=False)

    choise_bypass = forms.BooleanField(label='Функция Bypass',
                                       help_text=u'Добавляет в схему дополнительные изделия для реализации Bypass',
                                       required=False
                                       )

    atributes = forms.ChoiceField(choices=TYPE_COMMUNICATION, widget = forms.Select(attrs={'class': 'form-control'}),
                                  )

    manufacturer = forms.ModelChoiceField(queryset=ItemManufacturer.objects.all()\
                                            .values_list('name', flat=True).distinct(),
                                            required=False,
                                            widget=forms.Select(attrs={'class': 'form-control'})
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
