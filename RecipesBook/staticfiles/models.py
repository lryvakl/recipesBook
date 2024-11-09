

# Create your models here.
from django.db import models

class Recipe(models.Model):
    name = models.CharField('Name',max_length=255)
    ingredients = models.TextField('Ingredients')
    instructions = models.TextField('Instructions')
    category = models.CharField('category',max_length=50)

    def __str__(self):
        return self.name
