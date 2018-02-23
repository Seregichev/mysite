# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-22 19:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_hstore.fields
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cms', '0019_auto_20180222_2227'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelloPluginSetting',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='database_item_hellopluginsetting', serialize=False, to='cms.CMSPlugin')),
                ('welcome', models.CharField(blank=True, max_length=128, null=True, verbose_name='Приветсвие')),
                ('afterword', models.TextField(blank=True, max_length=256, null=True, verbose_name='Послесовие')),
                ('unnamed_name', models.CharField(blank=True, max_length=128, null=True, verbose_name='Имя неавторизованного')),
                ('tag_class', models.CharField(blank=True, max_length=256, null=True, verbose_name='HTML класс')),
                ('tag_style', models.CharField(blank=True, max_length=256, null=True, verbose_name='HTML стиль')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series', models.CharField(blank=True, default=None, max_length=64, null=True, verbose_name='Серия')),
                ('name', models.CharField(blank=True, default=None, max_length=64, null=True, verbose_name='Название')),
                ('vendor_code', models.CharField(blank=True, default=None, max_length=64, null=True, verbose_name='Артикул')),
                ('description', models.TextField(blank=True, default=None, null=True, verbose_name='Описание')),
                ('voltage', models.DecimalField(decimal_places=0, default=0, max_digits=7, verbose_name='Напряжение [В]')),
                ('current', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Ток [А]')),
                ('type_current', models.CharField(blank=True, choices=[('AC', 'AC'), ('DC', 'DC')], default='AC', max_length=3, null=True, verbose_name='Вид тока')),
                ('power', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Мощность [кВт]')),
                ('temperature_protect', models.CharField(blank=True, choices=[('10', '10'), ('20', '20'), ('30', '30'), ('40', '40')], default=None, max_length=3, null=True, verbose_name='Класс тепловой защиты')),
                ('force_input', models.DecimalField(decimal_places=0, default=0, max_digits=2, verbose_name='Силовые входы [шт]')),
                ('discret_input', models.DecimalField(decimal_places=0, default=0, max_digits=4, verbose_name='Дискретные входы [шт]')),
                ('discret_output', models.DecimalField(decimal_places=0, default=0, max_digits=4, verbose_name='Дискретные выходы [шт]')),
                ('analog_input', models.DecimalField(decimal_places=0, default=0, max_digits=4, verbose_name='Аналоговые входы [шт]')),
                ('analog_output', models.DecimalField(decimal_places=0, default=0, max_digits=4, verbose_name='Аналоговые выходы [шт]')),
                ('temperature_input', models.DecimalField(decimal_places=0, default=0, max_digits=4, verbose_name='Температурные входы [шт]')),
                ('height', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Высота')),
                ('width', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Ширина')),
                ('depth', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Глубина')),
                ('area', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Площадь')),
                ('atributes', django_hstore.fields.DictionaryField(blank=True, default=None, null=True, verbose_name='Атрибуты')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно?')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='---Цена---')),
                ('currency', models.CharField(blank=True, default=None, max_length=64, null=True, verbose_name='Валюта')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Обновленно')),
            ],
            options={
                'verbose_name': 'Изделие',
                'verbose_name_plural': 'Изделия',
            },
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=64, null=True, verbose_name='Название')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='database_item.ItemCategory', verbose_name='Родитель')),
            ],
            options={
                'verbose_name': 'Категория изделия',
                'verbose_name_plural': 'Категории изделий',
            },
        ),
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='items_images/', verbose_name='Изображение')),
                ('is_main', models.BooleanField(default=False, verbose_name='Основное?')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно?')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Обновленно')),
                ('item', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='database_item.Item', verbose_name='Изделие')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
            },
        ),
        migrations.CreateModel(
            name='ItemManufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(blank=True, default=None, max_length=5, null=True, verbose_name='Сокращение')),
                ('name', models.CharField(blank=True, default=None, max_length=64, null=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Производитель изделия',
                'verbose_name_plural': 'Производители изделий',
            },
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='database_item.ItemCategory', verbose_name='Категория'),
        ),
        migrations.AddField(
            model_name='item',
            name='manufacturer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='database_item.ItemManufacturer', verbose_name='Производитель'),
        ),
    ]
