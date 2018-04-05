# -*- coding: utf-8 -*-
from django import forms
from database_item.models import Item, ItemManufacturer
from django.contrib.auth import authenticate
from .models import CustomUser
from django.contrib.auth.models import User


class LoginForm (forms.Form):

    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': u'Ваш логин', 'class': 'form-control', 'id': 'inputLogin', 'type': 'text'}),
                              )

    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'placeholder': u'Ваш пароль', 'class': 'form-control', 'id': 'inputPassword', 'type': 'password'}),
                               )

    remember_me = forms.BooleanField(label='Запомнить меня', required=False)

    def clean(self):
        if not self._errors:
            cleaned_data = super(LoginForm, self).clean()
            username = cleaned_data.get('username')
            password = cleaned_data.get('password')
            try:
                user = User.objects.get(username=username)
                if not user.check_password(password):
                    raise forms.ValidationError(u'Неверное сочетание e-mail \ Пароль.')
                elif not user.is_active:
                    raise forms.ValidationError(u'Пользователь с таким e-mail заблокирован.')
            except User.DoesNotExist:
                raise forms.ValidationError(u'Пользователь с таким Логином не существует.')
            return cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user