# Generated by Django 5.1.3 on 2024-11-07 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default='main/media/image.png', upload_to='recipe_images/'),
        ),
    ]
