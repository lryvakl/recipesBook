import requests
from django.conf import settings

BASE_URL = 'https://api.spoonacular.com/recipes'

def get_recipe_by_name(name):
    """
    Отримання рецепту за назвою з Spoonacular API.
    """
    # Спершу шукаємо рецепт за назвою
    url = f"{BASE_URL}/complexSearch"
    params = {
        'query': name,
        'apiKey': settings.SPOONACULAR_API_KEY,
        'number': 1  # Отримуємо лише перший результат
    }
    search_response = requests.get(url, params=params)

    if search_response.status_code == 200:
        results = search_response.json().get('results', [])
        if results:
            recipe_id = results[0].get('id')
            if recipe_id:
                # Отримуємо детальну інформацію про рецепт
                detail_url = f"{BASE_URL}/{recipe_id}/information"
                detail_response = requests.get(detail_url, params={'apiKey': settings.SPOONACULAR_API_KEY})

                if detail_response.status_code == 200:
                    recipe_data = detail_response.json()

                    # Формуємо результат
                    return [{
                        'id': recipe_data.get('id'),
                        'name': recipe_data.get('title', 'No Title'),
                        'ingredients': ', '.join([i['original'] for i in recipe_data.get('extendedIngredients', [])]),
                        'instructions': recipe_data.get('instructions', 'No instructions available'),
                        'category': recipe_data.get('dishTypes', ['Uncategorized'])[0],
                        'image_url': recipe_data.get('image', 'No image'),
                        'sourceUrl': recipe_data.get('sourceUrl', '#'),

                    }]

    # Якщо щось пішло не так
    return {'error': search_response.json()}
