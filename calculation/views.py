# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import ListView
from .models import Calculate, ItemInEstimate, ItemInCalculate
from database_item.models import ItemManufacturer

class CalculateList(ListView):
    template_name = "apps/calculate.html"

    context_object_name = 'calculates'

    def get_queryset(self):
        return Calculate.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CalculateList, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['item_in_calculate'] = ItemInCalculate.objects.filter(calculate__user=self.request.user)
        return context

class EstimateList(ListView):
    template_name = "apps/estimate.html"

    context_object_name = 'estimate'

    def get_queryset(self):
        return ItemInEstimate.objects.filter(user=self.request.user)