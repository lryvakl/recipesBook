from django.shortcuts import render
from .models import Recipe
from django.shortcuts import redirect
from fuzzysearch import find_near_matches

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

        return redirect('about-us')  # Перенаправляємо на головну сторінку після додавання рецепту

    return render(request, 'main/addRecipe.html')



def search_recipes(request):

    query = request.GET.get('q', '')  # Отримуємо значення з форми пошуку
    if query:
        recipes = Recipe.objects.filter(name__icontains=query)  # Фільтруємо рецепти за назвою
    else:
        recipes = Recipe.objects.all()  # Якщо запит порожній, виводимо всі рецепти

    return render(request, 'main/about.html', {'recipes': recipes})



def search_ingredients(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            if find_near_matches(query, recipe.ingredients, max_l_dist=2):  # max_l_dist визначає відстань редагування
                results.append(recipe)
    return render(request, 'main/index.html', {'results': results, 'query': query})


def search_ingredients2(request):
    query = request.GET.get('q', '')  # Отримання пошукового запиту або порожнього рядка
    results = []
    if query:
        results = Recipe.objects.filter(ingredients__icontains=query)  # Пошук за частковим збігом
    return render(request, 'main/index.html', {'results': results, 'query': query})


def search_ingredients0(request):
    query = request.GET.get('q', '').lower()  # Отримуємо та знижуємо регістр запиту
    if query:
        recipes = Recipe.objects.filter(ingredients__icontains=query)  # Фільтруємо рецепти за інгредієнтами
    else:
        recipes = Recipe.objects.all()  # Якщо запит порожній, виводимо всі рецепти

    return render(request, 'main/index.html', {'recipes': recipes})  # Відображаємо результат на головній сто