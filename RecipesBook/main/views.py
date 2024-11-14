from django.shortcuts import render
import csv
import re
from .models import Recipe
from django.shortcuts import redirect
from fuzzysearch import find_near_matches
from django.shortcuts import get_object_or_404, render

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



def search_recipes0(request):

    query = request.GET.get('q', '')  # Отримуємо значення з форми пошуку
    if query:
        recipes = Recipe.objects.filter(name__icontains=query)  # Фільтруємо рецепти за назвою
    else:
        recipes = Recipe.objects.all()  # Якщо запит порожній, виводимо всі рецепти

    return render(request, 'main/about.html', {'recipes': recipes})


def search_recipes(request):
    query = request.GET.get('q', '').strip()  # Отримуємо значення з форми пошуку та видаляємо зайві пробіли
    query = re.sub(r'[^\w\s,]', '', query)  # Видаляємо всі символи, крім літер, пробілів та ком
    query_name = [name.strip().lower() for name in
                         query.split(',')]  # Розбиваємо запит на інгредієнти

    if query:
        recipes = Recipe.objects.all()  # Перевірка на всі рецепти
        matching_recipes = []

        for recipe in recipes:
            recipe_name = [name.strip().lower() for name in
                                  recipe.name.split(',')]  # Аналогічно обробляємо інгредієнти рецепту
            if all(name in recipe_name for name in
                   query_name):  # Перевіряємо, чи всі інгредієнти з запиту є в рецепті
                matching_recipes.append(recipe)

        recipes = matching_recipes  # Повертаємо відповідні рецепти
    else:
        recipes = Recipe.objects.all()  # Якщо запит порожній, виводимо всі рецепти

    return render(request, 'main/about.html', {'recipes': recipes})


def search_ingredients0(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            if find_near_matches(query, recipe.ingredients, max_l_dist=2):  # max_l_dist визначає відстань редагування
                results.append(recipe)
    return render(request, 'main/index.html', {'results': results, 'query': query})


def search_ingredients1(request):
    query = request.GET.get('q', '').strip()
    query = re.sub(r'[^\w\s,]', '', query)  # Видаляємо всі символи, крім літер, пробілів та ком
    query_ingredients = [ingredient.strip().lower() for ingredient in
                         query.split(',')]  # Розбиваємо запит на інгредієнти

    results = []
    if query:
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            recipe_ingredients = [ingredient.strip().lower() for ingredient in
                                  recipe.ingredients.split(',')]  # Аналогічно обробляємо інгредієнти рецепту
            if all(ingredient in recipe_ingredients for ingredient in
                   query_ingredients):  # Перевіряємо, чи всі інгредієнти з запиту є в рецепті
                results.append(recipe)
    return render(request, 'main/index.html', {'results': results, 'query': query})


def search_ingredients(request):
    query = request.GET.get('q', '').strip()
    query = re.sub(r'[^\w\s,]', '', query)
    query_ingredients = {ingredient.strip().lower() for ingredient in query.split(',') if ingredient.strip()}

    results = []
    if query:
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            # Розділяємо інгредієнти рецепту на список
            recipe_ingredients = {ingredient.strip().lower() for ingredient in recipe.ingredients.split(',') if
                                  ingredient.strip()}
            missing_ingredients = query_ingredients - recipe_ingredients  # Інгредієнти, яких бракує в рецепті
            if query_ingredients & recipe_ingredients:
                # Додаємо розділені інгредієнти до результатів
                results.append({
                    'recipe': recipe,
                    'ingredients': recipe.ingredients.split(','),  # Передаємо як список
                    'missing_ingredients': missing_ingredients
                })
    return render(request, 'main/index.html', {'results': results, 'query': query})



