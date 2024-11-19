from django.shortcuts import render
import csv
import re
from .models import Recipe
from django.shortcuts import redirect
from fuzzysearch import find_near_matches
from django.shortcuts import get_object_or_404, render
from .services import get_recipe_by_name


def index(request):
    recipes = Recipe.objects.all()  # Завантаження всіх рецептів з бази
    return render(request, 'main/index.html', {'recipes': recipes})


def about(request):
    return render(request,'main/about.html')

def recipes_view(request):
    recipes = Recipe.objects.all()  # Отримуємо всі рецепти з бази даних
    return render(request, 'main/about.html', {'recipes': recipes})

def login(request):
    return render(request, 'main/login.html')


def register(request):
    return render(request, 'main/register.html')


def changePass(request):
    return render(request, 'main/changePass.html')


def profile(request):
    return render(request, 'main/profile.html')


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
    query = request.GET.get('q', '').strip()  # Отримуємо запит користувача
    query = re.sub(r'[^\w\s,]', '', query)  # Видаляємо зайві символи

    results = []

    if query:
        # Локальний пошук за назвою рецепту
        all_recipes = Recipe.objects.filter(
            name__icontains=query)  # Використовуємо __icontains для пошуку за частиною назви
        for recipe in all_recipes:
            results.append({
                'id': recipe.id,
                'name': recipe.name,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'category': recipe.category,
                'image': recipe.get_image_url(),
                'link': None,  # Немає посилання для локальних рецептів
            })

        # Пошук через Spoonacular API
        spoonacular_results = get_recipe_by_name(query)  # Запит до Spoonacular
        if 'error' not in spoonacular_results:
            for recipe in spoonacular_results:
                results.append({
                    'id': None,  # Немає локального ID для Spoonacular
                    'name': recipe['name'],
                    'ingredients': recipe['ingredients'],
                    'instructions': recipe['instructions'],
                    'category': recipe['category'],
                    'image': recipe['image_url'],

                })

    # Повертаємо шаблон із результатами
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