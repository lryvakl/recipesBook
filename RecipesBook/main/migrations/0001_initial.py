# Generated by Django 5.1.3 on 2024-11-07 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('ingredients', models.TextField(verbose_name='Ingredients')),
                ('instructions', models.TextField(verbose_name='Instructions')),
                ('category', models.CharField(max_length=50, verbose_name='category')),
            ],
        ),
    ]