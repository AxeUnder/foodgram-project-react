# recipes/management/commands/import_csv.py
import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

ModelsCSV = {
    Ingredient: 'ingredients.csv',
}

EXPECTED_HEADER = ['name', 'measurement_unit']


class Command(BaseCommand):
    help = 'Импорт данных из csv файлов'

    def handle(self, *args, **options):
        for model, csv_files in ModelsCSV.items():
            model.objects.all().delete()
            path_to_file = f'{settings.CSV_DIR}/{csv_files}'
            print(f'Начат импорт данных из файла {path_to_file}')
            with open(
                path_to_file,
                mode='r',
                encoding='utf-8',
            ) as csv_file:
                reader = csv.DictReader(csv_file)

                header = reader.fieldnames
                if header != EXPECTED_HEADER:
                    raise ValueError(
                        'Неверный формат файла: неправильные заголовки полей.')

                model.objects.bulk_create(model(**data) for data in reader)
            self.stdout.write(
                f'Завершен импорт данных в модель {model.__name__}'
            )
            return 'Импорт всех данных завершен.'
