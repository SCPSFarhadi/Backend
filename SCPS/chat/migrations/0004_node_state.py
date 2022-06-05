# Generated by Django 4.0.2 on 2022-04-13 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('setT', models.CharField(max_length=200)),
                ('node_state', models.CharField(max_length=200)),
                ('fanCoilTem', models.CharField(max_length=200)),
                ('homeTem', models.CharField(max_length=200)),
                ('neighbors', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DateTime', models.DateTimeField()),
                ('temperature', models.CharField(max_length=200)),
                ('Node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.node')),
            ],
        ),
    ]