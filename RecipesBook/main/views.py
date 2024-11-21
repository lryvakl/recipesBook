from dbm import error

from django.conf import settings
from django.shortcuts import render
import csv
import re
from django.views.generic import FormView, CreateView
from .models import Recipe
from django.shortcuts import redirect
from fuzzysearch import find_near_matches
from django.shortcuts import get_object_or_404, render
from .services import get_recipe_by_name
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from django.urls import reverse_lazy



def index(request):
    recipes = Recipe.objects.all()  # Завантаження всіх рецептів з бази
    return render(request, 'main/index.html', {'recipes': recipes})


def about(request):
    return render(request,'main/about.html')

def recipes_view(request):
    recipes = Recipe.objects.all()  # Отримуємо всі рецепти з бази даних
    return render(request, 'main/about.html', {'recipes': recipes})

def recipe_detail(request, id):
    # Отримуємо рецепт з бази даних за ID
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, 'main/recipe_detail.html', {'recipe': recipe})


def recipe_detail_spoonacular(request, title):
    # Використовуємо slug замість id
    url = f"https://api.spoonacular.com/recipes/complexSearch"
    response = requests.get(url, params={'query': title, 'apiKey': settings.SPOONACULAR_API_KEY})

    if response.status_code == 200:
        recipe = response.json().get('results', [])[0]  # Припускаємо, що це перший результат
        return render(request, 'main/recipe_detail.html', {'recipe': recipe})
    else:
        return render(request, 'error.html', {'message': 'Recipe not found.'})


def login(request):
    return render(request, 'main/login.html')


def changePass(request):
    return render(request, 'main/changePass.html')


@login_required
def profile(request):

    # Отримуємо всі улюблені рецепти поточного користувача
    favorite_recipes = request.user.favorite_recipes.all()  # related_name='favorite_recipes'

    # Передаємо список улюблених рецептів у контекст
    context = {
        'favorite_recipes': favorite_recipes,
    }
    return render(request, 'main/profile.html', context)

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Зберігаємо користувача в базі
        user = form.save()
        return super().form_valid(form)




def addRecipe(request):
    return render(request, 'main/addRecipe.html')



def add_recipe(request):
    if request.method == "POST":

        name = request.POST.get('name')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        # Створення нового рецепту в базі даних
        new_recipe = Recipe.objects.create(
            name=name,
            ingredients=ingredients,
            instructions=instructions,
            category=category,
            image = image
        )

        return redirect('about-us')

    return render(request, 'main/addRecipe.html')



def search_recipes(request):
    query = request.GET.get('q', '').strip()  # Отримуємо параметр пошуку
    results = []

    # Завантажуємо всі рецепти з вашої бази
    if query:
        # Якщо є пошуковий запит, фільтруємо за ім'ям
        local_recipes = Recipe.objects.filter(name__icontains=query)
    else:
        # Якщо запиту немає, показуємо всі рецепти
        local_recipes = Recipe.objects.all()

    for recipe in local_recipes:
        results.append({
            'id': recipe.id,
            'name': recipe.name,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'category': recipe.category,
            'image': recipe.get_image_url,
            'link': None,  # Локальні рецепти не мають зовнішнього посилання
        })

    # Пошук через Spoonacular
    if query:  # Якщо є запит, шукаємо за ім'ям і для Spoonacular
        spoonacular_results = get_recipe_by_name(query)
    else:
        spoonacular_results = get_recipe_by_name("")  # Пошук без параметрів для Spoonacular

    if 'error' not in spoonacular_results:  # Перевірка на помилки у відповіді від Spoonacular
        for recipe in spoonacular_results:
            results.append({
                'id': None,  # Рецепт з Spoonacular не має локального ID
                'name': recipe['name'],
                'ingredients': recipe['ingredients'],
                'instructions': recipe['instructions'],
                'category': recipe.get('category', 'Unknown'),
                'image': recipe['image_url'],
                'link': recipe.get('sourceUrl', '#'),  # Додаємо посилання на Spoonacular
            })

    return render(request, 'main/about.html', {'recipes': results})


def search_ingredients(request):
    query = request.GET.get('q', '').strip()  # Отримуємо запит користувача
    query = re.sub(r'[^\w\s,]', '', query)  # Видаляємо зайві символи
    query_ingredients = {ingredient.strip().lower() for ingredient in query.split(',') if ingredient.strip()}  # Форматування

    results = []

    if query:
        # Локальний пошук за інгредієнтами
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            recipe_ingredients = {ingredient.strip().lower() for ingredient in recipe.ingredients.split(',') if ingredient.strip()}
            if query_ingredients & recipe_ingredients:  # Якщо є хоча б один збіг
                results.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'ingredients': ', '.join(recipe_ingredients),
                    'instructions': recipe.instructions,
                    'category': recipe.category,
                    'image': recipe.get_image_url(),
                })

        # Пошук через Spoonacular API
        spoonacular_results = get_recipe_by_name(query)  # Запит до Spoonacular
        if 'error' not in spoonacular_results:
            for recipe in spoonacular_results:
                recipe_ingredients = {ingredient.strip().lower() for ingredient in recipe['ingredients'].split(',') if ingredient.strip()}
                if query_ingredients & recipe_ingredients:  # Якщо є хоча б один збіг
                    results.append({
                        'id': None,  # Немає локального ID для Spoonacular
                        'name': recipe['name'],
                        'ingredients': recipe['ingredients'],
                        'instructions': recipe['instructions'],
                        'category': recipe['category'],
                        'image': recipe['image_url'],
                    })

    return render(request, 'main/index.html', {'results': results, 'query': query})



def add_to_favorites(request, id):
    # Отримуємо рецепт за ID
    recipe = get_object_or_404(Recipe, id=id)

    # Додаємо цей рецепт до улюблених поточного користувача
    if request.user.is_authenticated:
        recipe.favorite_by_users.add(request.user)
        return redirect('recipe_detail', id=id)
    else:
        # Перенаправляємо неавторизованих користувачів на сторінку входу
        return redirect('login')



@login_required



def remove_from_favorites(request, id):
    # Отримуємо рецепт за ID
    recipe = get_object_or_404(Recipe, id=id)

    # Видаляємо рецепт із улюблених користувача
    recipe.favorite_by_users.remove(request.user)

    # Перенаправлення назад на сторінку профілю
    return redirect('profile')



def add_to_favorites_spoonacular(request, title):
    # Отримуємо дані рецепту з Spoonacular за назвою
    url = f"https://api.spoonacular.com/recipes/complexSearch"
    response = requests.get(url, params={'query': title, 'apiKey': settings.SPOONACULAR_API_KEY, 'number': 1})

    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            recipe_data = results[0]

            # Створюємо або знаходимо рецепт у базі
            recipe, created = Recipe.objects.get_or_create(
                name=recipe_data.get('title', 'No Title'),
                defaults={  # Використовуємо defaults для інших полів
                    'ingredients': ', '.join(
                        [i['original'] for i in recipe_data.get('extendedIngredients', [])]) if recipe_data.get(
                        'extendedIngredients') else 'No ingredients',
                    'instructions': recipe_data.get('instructions', 'No instructions available'),
                    'category': recipe_data.get('dishTypes', ['Uncategorized'])[0],  # Категорія
                    'image': recipe_data.get('image', ''),  # Картинка
                }
            )

            # Додаємо рецепт до улюблених
            recipe.favorite_by_users.add(request.user)

            # Перенаправляємо на сторінку рецепту
            return redirect('recipe_detail', recipe.id)

    # Якщо не знайдено рецепт
    return render(request, 'error.html', {'message': 'Recipe not found.'})


