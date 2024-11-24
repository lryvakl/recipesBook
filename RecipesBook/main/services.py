import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.spoonacular.com/recipes'

def get_recipe_by_name(name, number=10):
    """
    Отримання рецептів за назвою з Spoonacular API.
    """
    # Запит на пошук рецептів за назвою
    url = f"{BASE_URL}/complexSearch"
    params = {
        'query': name,
        'apiKey': settings.SPOONACULAR_API_KEY,
        'number': number  # Кількість рецептів, які потрібно отримати
    }
    search_response = requests.get(url, params=params)

    if search_response.status_code == 200:
        results = search_response.json().get('results', [])
        recipes = []

        for result in results:
            id = result.get('id')
            name = result.get('title', 'No Title')
            image_url = result.get('image', 'No image')

            if id:
                # Отримання детальної інформації про кожен рецепт
                detail_url = f"{BASE_URL}/{id}/information"
                detail_response = requests.get(detail_url, params={'apiKey': settings.SPOONACULAR_API_KEY})

                if detail_response.status_code == 200:
                    recipe = detail_response.json()
                    recipes.append({
                        'id': recipe.get('id'),
                        'name': recipe.get('title', name),
                        'ingredients': ', '.join([i.get('original', 'Unknown ingredient') for i in recipe.get('extendedIngredients', [])]),
                        'instructions': recipe.get('instructions', 'No instructions available'),
                        'category': recipe.get('dishTypes', ['Uncategorized'])[0] if recipe.get('dishTypes') else 'Uncategorized',
                        'image_url': recipe.get('image', image_url),
                        'sourceUrl': recipe.get('sourceUrl', '#'),
                    })
                    logger.info(f"Fetched recipe ID: {recipe.get('id')}")
                else:
                    logger.error(f"Failed to fetch details for recipe ID: {id}, Status code: {detail_response.status_code}")
                    recipes.append({
                        'id': id,
                        'name': name,
                        'ingredients': 'Unable to fetch ingredients.',
                        'instructions': 'Unable to fetch instructions.',
                        'category': 'Uncategorized',
                        'image_url': image_url,
                        'sourceUrl': '#',
                    })
        print(f"Searching recipes with query: {name}")

        return recipes

    # Обробка інших статусів
    if search_response.status_code == 403:
        logger.error("Access forbidden. Check your API key.")
        return {'error': 'Access forbidden. Check your API key.'}
    elif search_response.status_code == 429:
        logger.warning("Rate limit exceeded. Please wait before making more requests.")
        return {'error': 'Rate limit exceeded. Please wait before making more requests.'}
    else:
        logger.error(f"Unexpected error: {search_response.status_code}")
        return {'error': search_response.json()}
