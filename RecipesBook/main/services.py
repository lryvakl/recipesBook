import requests
from django.conf import settings

BASE_URL = 'https://api.spoonacular.com/recipes'

def get_recipe_by_name(name):
    """
    Отримання рецепту за назвою з Spoonacular API.
    """
    url = f"{BASE_URL}/complexSearch"
    params = {
        'query': name,
        'addRecipeInformation': True,  # Запит на додаткову інформацію про рецепт
        'apiKey': settings.SPOONACULAR_API_KEY,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json().get('results', [])
        recipes = []
        for recipe in data:
            # Перевіряємо наявність усіх необхідних полів
            title = recipe.get('title', 'No Title')
            ingredients = ', '.join([i['original'] for i in recipe.get('extendedIngredients', [])]) if recipe.get('extendedIngredients') else 'No ingredients'
            instructions = recipe.get('instructions', 'No instructions available') if recipe.get('instructions') else 'No instructions available'
            category = recipe.get('dishTypes', ['Uncategorized'])[0] if recipe.get('dishTypes') else 'Uncategorized'
            image_url = recipe.get('image', 'No image')
            source_url = recipe.get('sourceUrl', '#')  # Додаємо посилання на джерело рецепту

            recipes.append({
                'name': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'category': category,
                'image_url': image_url,
                'sourceUrl': source_url,
            })
        return recipes
    else:
        return {'error': response.json()}
