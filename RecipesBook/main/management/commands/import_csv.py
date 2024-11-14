from django.core.management.base import BaseCommand
from main.models import Recipe
import csv



class Command(BaseCommand):
    help = 'Imports recipes from CSV file'

    def handle(self, *args, **kwargs):
        with open('data/data.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not Recipe.objects.filter(name=row['Title']).exists():
                    recipe = Recipe(
                        name=row['Title'],
                        ingredients=row['Ingredients'],
                        instructions=row['Instructions'],
                        image=row['Image_Name'],
                    )
                    recipe.save()

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
