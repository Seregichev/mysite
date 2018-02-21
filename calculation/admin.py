# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Calculate, ItemInCalculate, ItemInEstimate

class ItemInCalculateInline(admin.TabularInline):
    model = ItemInCalculate
    extra = 0

class CalculateAdmin (admin.ModelAdmin):

    list_display = [field.name for field in Calculate._meta.fields]
    list_filter = ['calculate_name']
    search_fields = ['calculate_name', 'user__username', 'user__first_name', 'user__last_name', 'total_price', 'created']
    inlines = [ItemInCalculateInline]


    class Meta:
        model = Calculate

admin.site.register(Calculate, CalculateAdmin)

class ItemInCalculateAdmin (admin.ModelAdmin):

    list_display = [field.name for field in ItemInCalculate._meta.fields]

    class Meta:
        model = ItemInCalculate

admin.site.register(ItemInCalculate, ItemInCalculateAdmin)

class ItemInEstimateAdmin (admin.ModelAdmin):

    list_display = [field.name for field in ItemInEstimate._meta.fields]

    class Meta:
        model= ItemInEstimate

admin.site.register(ItemInEstimate, ItemInEstimateAdmin)
