
import os
# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    name = models.CharField('Name',max_length=255)
    ingredients = models.TextField('Ingredients')
    instructions = models.TextField('Instructions')
    category = models.CharField('category',max_length=50)
    image = models.ImageField('Image', upload_to='media/', blank=True, null=True)
    image_url = models.CharField('Image URL', max_length=500, blank=True, null=True)
    favorite_by_users = models.ManyToManyField(User, related_name='favorite_recipes', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_image_url(self):
        if self.image:
            return self.image.url  # Використовуємо вбудовану властивість .url для коректного шляху
        return '/static/default_image.jpg'  # Якщо зображення немає, покажемо зображення за замовчуванням

    def __str__(self):
        return self.name
