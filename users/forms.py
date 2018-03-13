# -*- coding: utf-8 -*-
from django import forms
from database_item.models import Item, ItemManufacturer
from django.contrib.auth import authenticate


class LoginForm (forms.Form):

    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': u'Ваш логин', 'class': 'form-control', 'id': 'inputLogin', 'type': 'text'}),
                              )

    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'placeholder': u'Ваш пароль', 'class': 'form-control', 'id': 'inputPassword', 'type': 'password'}),
                               )

    remember_me = forms.BooleanField(label='Запомнить меня', required=False)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user