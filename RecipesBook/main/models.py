
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
    favorite_by_users = models.ManyToManyField(User, related_name='favorite_recipes', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)


    def get_image_url(self):
        # Перевіряємо, чи має файл розширення
        if not self.image.name.endswith('.jpg'):
            return os.path.join('/media/', self.image.name + '.jpg')
        return os.path.join('/media/', self.image.name)

    def __str__(self):
        return self.name
