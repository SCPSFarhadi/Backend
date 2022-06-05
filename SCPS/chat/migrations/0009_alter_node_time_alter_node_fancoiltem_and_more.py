# Generated by Django 4.0.2 on 2022-06-05 07:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_alter_node_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='Time',
            field=models.CharField(blank=True, default='none', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='node',
            name='fanCoilTem',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='node',
            name='homeTem',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='node',
            name='neighbors',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='node',
            name='node_state',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='node',
            name='setT',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='state',
            name='DateTime',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='state',
            name='Node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.node'),
        ),
        migrations.AlterField(
            model_name='state',
            name='temperature',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]