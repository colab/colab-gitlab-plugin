# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_gitlab', '0002_auto_20151210_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitlabUser',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('username', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Gitlab User',
                'verbose_name_plural': 'Gitlab User',
            },
            bases=(models.Model,),
        ),
    ]
