# Generated by Django 3.2.3 on 2023-08-04 10:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_follower'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follower',
            options={'ordering': ('id',), 'verbose_name': 'Подписчик', 'verbose_name_plural': 'Подписчики'},
        ),
    ]