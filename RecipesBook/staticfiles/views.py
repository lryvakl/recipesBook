from django.shortcuts import render
from .models import Recipe
from django.shortcuts import redirect

def index(request):
    return render(request,'main/index.html')


def about(request):
    recipes = Recipe.objects.all()
    return render(request,'main/about.html',  {'recipes': recipes})


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

        # Створення нового рецепту в базі даних
        new_recipe = Recipe.objects.create(
            name=name,
            ingredients=ingredients,
            instructions=instructions,
            category=category
        )

        return redirect('about-us')  # Перенаправляємо на головну сторінку після додавання рецепту

    return render(request, 'main/addRecipe.html')