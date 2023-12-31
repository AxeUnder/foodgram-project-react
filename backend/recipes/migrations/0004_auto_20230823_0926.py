# Generated by Django 3.2.3 on 2023-08-23 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230823_0806'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='is_favorited',
            field=models.BooleanField(blank=True, default=False, verbose_name='Добавить в избранное'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='is_in_shopping_cart',
            field=models.BooleanField(blank=True, default=False, verbose_name='Добавить в покупки'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выставите теги', related_name='recipes', to='recipes.Tag', verbose_name='Список тегов'),
        ),
    ]
