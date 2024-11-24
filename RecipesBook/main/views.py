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
from fuzzywuzzy import fuzz
from operator import itemgetter


def index(request):
    recipes = Recipe.objects.all()  # Завантаження всіх рецептів з бази
    return render(request, 'main/index.html', {'recipes': recipes})


def about(request):
    return render(request,'main/about.html')



def recipes_view(request):
    query = request.GET.get('q', '').strip()
    results = []

    # Завантаження рецептів зі Spoonacular
    spoonacular_results = get_recipe_by_name(query if query else "")
    spoonacular_recipe_names = set()

    if 'error' not in spoonacular_results:
        for recipe in spoonacular_results:
            results.append({

                'name': recipe.get('name'),
                'ingredients': recipe['ingredients'],
                'instructions': recipe['instructions'],
                'category': recipe.get('category', 'Unknown'),
                'image': recipe['image_url'],
                'link': recipe.get('sourceUrl', '#'),
            })
            spoonacular_recipe_names.add(recipe['name'].lower())

    # Завантаження рецептів з локальної бази
    local_recipes = Recipe.objects.filter(name__icontains=query) if query else Recipe.objects.all()
    for recipe in local_recipes:
        if recipe.name.lower() not in spoonacular_recipe_names:
            results.append({
                'id': recipe.id,
                'name': recipe.name,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'category': recipe.category,
                'image': recipe.get_image_url(),
                'link': None,
            })

    return render(request, 'main/about.html', {'recipes': results})




def recipe_detail(request, id):
    # Отримуємо рецепт з бази даних за ID
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, 'main/recipe_detail.html', {'recipe': recipe})


from django.shortcuts import redirect


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
            source_url = results[0].get('sourceUrl', '#')
            if recipe_id:
                # Отримання детальної інформації про рецепт
                detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
                detail_response = requests.get(detail_url, params={'apiKey': settings.SPOONACULAR_API_KEY})

                if detail_response.status_code == 200:
                    recipe = detail_response.json()



                    context = {
                        'recipe': {
                            'name': recipe.get('title', 'No name available'),
                            'ingredients': recipe.get('extendedIngredients', []),
                            'instructions': recipe.get('instructions', 'No instructions available'),
                            'category': recipe.get('dishTypes', ['Unknown'])[0],
                            'image_url': recipe.get('image', '/static/default_image.jpg'),
                            'source_url': recipe.get('sourceUrl', '#')  # Додано джерело

                        }
                    }
                    return render(request, 'main/recipe_detail.html', context)

                elif source_url and source_url != '#':
                    return redirect(source_url)

 # Якщо рецепт не знайдено в Spoonacular
    return render(request, 'main/recipe_detail.html')




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




def addRecipe(request):
    return render(request, 'main/addRecipe.html')



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
