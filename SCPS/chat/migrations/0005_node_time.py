# Generated by Django 4.0.2 on 2022-04-13 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_node_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='Time',
            field=models.CharField(default='none', max_length=200),
        ),
    ]
