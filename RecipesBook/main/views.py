from dbm import error
import csv
import re
from django.views.generic import CreateView
from .models import Recipe
from django.shortcuts import get_object_or_404
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
from fuzzywuzzy import fuzz
from operator import itemgetter




def recipes_view(request):
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort_by', '').strip()  # Параметр сортування
    category_filter = request.GET.get('category', '').strip()  # Параметр фільтру категорії
    results = []

    # Завантаження рецептів зі Spoonacular
    spoonacular_results = []
    if query:
        spoonacular_results = get_recipe_by_name(query)
    else:
        try:
            random_url = "https://api.spoonacular.com/recipes/random"
            params = {
                "apiKey": settings.SPOONACULAR_API_KEY,
                "number": 3,  # Кількість випадкових рецептів
            }
            response = requests.get(random_url, params=params)
            if response.status_code == 200:
                data = response.json()
                spoonacular_results = data.get("recipes", [])
        except Exception as e:
            print(f"Error during Spoonacular random recipes fetch: {e}")

    spoonacular_recipe_names = set()
    if 'error' not in spoonacular_results:
        for recipe in spoonacular_results:
            recipe_category = recipe.get('dishTypes', ['Uncategorized'])[0] if recipe.get('dishTypes') else 'Uncategorized'
            if not category_filter or category_filter.lower() in recipe_category.lower():
                results.append({
                    'name': recipe.get('title', recipe.get('name')),  # Використовуємо "title" або "name"
                    'ingredients': ', '.join([i.get('original', 'Unknown ingredient') for i in recipe.get('extendedIngredients', [])]),
                    'instructions': recipe.get('instructions', 'No instructions available'),
                    'category': recipe_category,
                    'image': recipe.get('image', ''),
                    'link': recipe.get('sourceUrl', '#'),
                })
            spoonacular_recipe_names.add(recipe.get('name', '').lower())

    # Завантаження рецептів з локальної бази
    local_recipes = Recipe.objects.filter(name__icontains=query) if query else Recipe.objects.all()
    for recipe in local_recipes:
        if recipe.name.lower() not in spoonacular_recipe_names:
            if not category_filter or category_filter.lower() in recipe.category.lower():
                results.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'ingredients': recipe.ingredients,
                    'instructions': recipe.instructions,
                    'category': recipe.category,
                    'image': recipe.get_image_url(),
                    'link': None,
                })

    # Сортування результатів
    if sort_by == 'name':
        results.sort(key=lambda x: x['name'])
    elif sort_by == 'category':
        results.sort(key=lambda x: x['category'])

    # Отримання всіх унікальних категорій для випадаючого списку
    all_categories = set(r['category'] for r in results if r.get('category'))

    return render(request, 'main/about.html', {
        'recipes': results,
        'sort_by': sort_by,
        'categories': sorted(all_categories),
        'selected_category': category_filter
    })


def recipe_detail(request, id):
    # Отримуємо рецепт з бази даних за ID
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, 'main/recipe_detail.html', {'recipe': recipe})


from django.conf import settings
from django.shortcuts import render, redirect
import requests


def recipe_detail_spoonacular(request, title):
    # Пошук рецепта за назвою
    search_url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        'query': title,
        'apiKey': settings.SPOONACULAR_API_KEY,
        'number': 1  # Отримати лише перший результат
    }

    search_response = requests.get(search_url, params=params)

    if search_response.status_code == 200:
        results = search_response.json().get('results', [])
        if results:  # Якщо знайдено хоча б один рецепт
            recipe_id = results[0].get('id')
            if recipe_id:
                # Отримання детальної інформації про рецепт
                detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
                detail_response = requests.get(detail_url, params={'apiKey': settings.SPOONACULAR_API_KEY})

                if detail_response.status_code == 200:
                    recipe = detail_response.json()

                    # Отримання харчової інформації
                    nutrition = recipe.get('nutrition', {}).get('nutrients', [])
                    calories = next((item['amount'] for item in nutrition if item['title'] == 'Calories'), 'N/A')
                    protein = next((item['amount'] for item in nutrition if item['title'] == 'Protein'), 'N/A')
                    fat = next((item['amount'] for item in nutrition if item['title'] == 'Fat'), 'N/A')
                    carbs = next((item['amount'] for item in nutrition if item['title'] == 'Carbohydrates'), 'N/A')

                    context = {
                        'recipe': {
                            'name': recipe.get('title', 'No name available'),
                            'ingredients': recipe.get('extendedIngredients', []),
                            'calories': calories,  # Передаємо значення нутрієнтів
                            'protein': protein,
                            'fat': fat,
                            'carbs': carbs,
                            'instructions': recipe.get('instructions', 'No instructions available'),
                            'category': recipe.get('dishTypes', ['Unknown'])[0],
                            'image_url': recipe.get('image', '/static/default_image.jpg'),
                            'source_url': recipe.get('sourceUrl', '#')  # Додано джерело
                        }
                    }
                    return render(request, 'main/recipe_detail.html', context)

    # Якщо рецепт не знайдено або сталася помилка
    return render(request, 'main/recipe_detail.html', {'error': 'Recipe not found or unavailable.'})


def login(request):
    return render(request, 'main/login.html')


def changePass(request):
    return render(request, 'main/changePass.html')


@login_required
def profile(request):

    user = request.user
    # Отримати рецепти, які створив користувач
    my_recipes = Recipe.objects.filter(author=user)
    # Отримуємо всі улюблені рецепти поточного користувача
    favorite_recipes = request.user.favorite_recipes.all()  # related_name='favorite_recipes'

    # Передаємо список улюблених рецептів у контекст
    context = {
        'user': user,
        'my_recipes': my_recipes,
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


@login_required
def add_recipe(request):
    if request.method == "POST":
        name = request.POST.get('name')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        # Створення нового рецепту в базі даних із вказаним автором
        new_recipe = Recipe.objects.create(
            name=name,
            ingredients=ingredients,
            instructions=instructions,
            category=category,
            image=image,
            author=request.user  # Додаємо автора
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
            'image': recipe.get_image_url(),  # Викликаємо метод для отримання реального URL
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
                'image': recipe['image_url'],  # URL зображення для рецептів з Spoonacular
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
            used_ingredients = query_ingredients & recipe_ingredients
            missed_ingredients = recipe_ingredients - used_ingredients
            if query_ingredients & recipe_ingredients:  # Якщо є хоча б один збіг
                results.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'ingredients': ', '.join(recipe_ingredients),
                    'used_ingredients': list(used_ingredients),  # Інгредієнти, які є
                    'missed_ingredients': list(missed_ingredients),
                    'match_count': len(used_ingredients),  # Кількість наявних інгредієнтів#
                    'instructions': recipe.instructions,
                    'category': recipe.category,
                    'image': recipe.get_image_url(),
                })

        # Пошук через Spoonacular API
        spoonacular_results = get_recipe_by_name(query)  # Запит до Spoonacular API
        if 'error' not in spoonacular_results:
            for recipe in spoonacular_results:
                # Нормалізуємо інгредієнти
                recipe_ingredients_raw = recipe.get('ingredients', '')
                if isinstance(recipe_ingredients_raw, list):
                    recipe_ingredients = {ingredient.strip().lower() for ingredient in recipe_ingredients_raw}
                else:
                    recipe_ingredients = {ingredient.strip().lower() for ingredient in recipe_ingredients_raw.split(',') if ingredient.strip()}

                # Порівнюємо інгредієнти, використовуючи схожість
                match_found = any(
                    any(fuzz.partial_ratio(query_ing, ri) > 80 for ri in recipe_ingredients)
                    for query_ing in query_ingredients
                )

                used_ingredients = query_ingredients & recipe_ingredients
                missed_ingredients = recipe_ingredients - used_ingredients

                if match_found:
                    results.append({
                        'id': None,  # Немає локального ID для Spoonacular
                        'name': recipe['name'],
                        'ingredients': ', '.join(recipe_ingredients),
                        'used_ingredients': list(used_ingredients),  # Інгредієнти, які є
                        'missed_ingredients': list(missed_ingredients),
                        'match_count': len(used_ingredients),  # Кількість наявних інгредієнтів
                        'instructions': recipe.get('instructions', 'No instructions provided.'),
                        'category': recipe.get('category', 'Uncategorized'),
                        'image': recipe.get('image_url', ''),
                    })

    results = sorted(results, key=itemgetter('match_count'), reverse=True)
    return render(request, 'main/index.html', {'results': results, 'query': query})


@login_required
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


def remove_from_favorites(request, id):
    # Отримуємо рецепт за ID
    recipe = get_object_or_404(Recipe, id=id)

    # Видаляємо рецепт із улюблених користувача
    recipe.favorite_by_users.remove(request.user)

    # Перенаправлення назад на сторінку профілю
    return redirect('profile')


@login_required
def add_to_favorites_spoonacular(request, title):
    # Формуємо запит до Spoonacular API
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        'query': title,
        'apiKey': settings.SPOONACULAR_API_KEY,
        'number': 1,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:  # Якщо знайдено хоча б один рецепт
            recipe_id = results[0].get('id')
            if recipe_id:
                # Отримання детальної інформації про рецепт
                detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
                detail_response = requests.get(detail_url, params={'apiKey': settings.SPOONACULAR_API_KEY})

                if detail_response.status_code == 200:
                    recipe = detail_response.json()

            if detail_response.status_code == 200:
                detail_data = detail_response.json()

                # Створюємо або знаходимо користувача "Spoonacular"
                spoonacular_user, created = User.objects.get_or_create(
                    username='spoonacular',
                    defaults={'email': 'spoonacular@example.com'}
                )

                # Отримуємо дані для рецепта
                name = detail_data.get('title', 'No Title')
                ingredients = ', '.join(
                    [i['original'] for i in detail_data.get('extendedIngredients', [])]
                ) if detail_data.get('extendedIngredients') else 'No ingredients'
                instructions = detail_data.get('instructions', 'No instructions available')
                category = detail_data.get('dishTypes', ['Uncategorized'])[0]
                image_url = detail_data.get('image', '')

                # Створюємо або знаходимо рецепт у базі
                recipe, created = Recipe.objects.get_or_create(
                    name=name,
                    defaults={
                        'ingredients': ingredients,
                        'instructions': instructions,
                        'category': category,
                        'image_url': image_url,
                        'author': spoonacular_user,
                    }
                )

                # Додаємо рецепт до улюблених поточного користувача
                recipe.favorite_by_users.add(request.user)

                # Перенаправляємо на сторінку рецепта
                return redirect('recipe_detail', recipe.id)

    # Якщо рецепт не знайдено
    return render(request, 'main/error.html', {'message': 'Recipe not found.'})


@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    recipe.delete()
    return redirect('profile')


import logging
logger = logging.getLogger(__name__)


def main_page(request):
    popular_recipes = []
    try:
        # Запит до Spoonacular
        popular_url = "https://api.spoonacular.com/recipes/random"
        params = {
            "apiKey": settings.SPOONACULAR_API_KEY,
            "number": 3
        }
        response = requests.get(popular_url, params=params)

        # Перевірка статусу відповіді
        if response.status_code == 200:
            data = response.json()
            popular_recipes = data.get("recipes", [])

            for recipe in popular_recipes:
                recipe["id"] = None
                recipe["name"] = recipe.get("title", "No title available")
                recipe["category"] = recipe.get("dishTypes", ['Uncategorized'])[0]
                recipe["ingredients"] = ', '.join([i.get('original', 'Unknown ingredient') for i in recipe.get('extendedIngredients', [])])
                recipe["image"] = recipe.get("image", "/static/default_image.jpg")
                recipe["instructions"] = recipe.get("instructions", "Instructions not available")
        else:
            logger.error(f"API error: {response.status_code}, {response.text}")
    except Exception as e:
        logger.exception(f"Помилка при запиті: {str(e)}")

    return render(request, "main/index.html", {"popular_recipes": popular_recipes})

