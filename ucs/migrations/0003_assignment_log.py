# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-17 14:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ucs', '0002_auto_20170907_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.CharField(blank=True, max_length=200, null=True)),
                ('finish_date', models.CharField(blank=True, max_length=200, null=True)),
                ('assignment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ucs.Assignment')),
                ('group_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ucs.Group')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ucs.User')),
            ],
        ),
    ]
