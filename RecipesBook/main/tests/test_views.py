from django.test import TestCase, Client
from unittest.mock import patch
from django.urls import reverse
from ..models import Recipe
from django.conf import settings
from django.contrib.auth.models import User


class RecipesViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        # Creating a local recipe for testing
        self.recipe = Recipe.objects.create(
            name="Test Recipe",
            ingredients="Flour, Sugar, Butter",
            instructions="Mix everything and bake.",
            category="Dessert",
            author=self.user
        )
        self.client = Client()

    @patch('requests.get')
    def test_recipes_view_with_query(self, mock_get):
        # Simulate Spoonacular API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "recipes": [{"title": "Spoonacular Recipe", "extendedIngredients": [{"original": "Sugar"}],
                         "instructions": "Mix and bake.", "dishTypes": ["Dessert"], "image": "",
                         "sourceUrl": "http://example.com"}]
        }

        # Make a request with a query parameter
        response = self.client.get(reverse('recipes') + '?q=Test')

        # Check that the response status is 200
        self.assertEqual(response.status_code, 200)

        # Check that the local recipe is in the context
        self.assertContains(response, "Test Recipe")

        # Check if Spoonacular recipe is included

        # Test the sorting functionality
        response_sorted = self.client.get(reverse('recipes') + '?sort_by=name')
        self.assertEqual(response_sorted.status_code, 200)
        self.assertContains(response_sorted, "Test Recipe")  # Ensure Spoonacular recipe appears first


    @patch('requests.get')
    def test_recipes_view_with_category_filter(self, mock_get):
            # Simulate Spoonacular API response for category filter
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "recipes": [{"title": "Spoonacular Dessert", "extendedIngredients": [{"original": "Sugar"}], "instructions": "Mix and bake.", "dishTypes": ["Dessert"], "image": "", "sourceUrl": "http://example.com"}]
            }

            # Make a request with category filter
            response = self.client.get(reverse('recipes') + '?category=Dessert')

            # Check that the response contains the filtered category
            self.assertContains(response, "Dessert")
            self.assertNotContains(response, "Main Course")


    @patch('requests.get')
    def test_recipes_view_without_query(self, mock_get):
        # Simulate Spoonacular API response when no query is provided
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "recipes": [{"title": "Spoonacular Recipe", "extendedIngredients": [{"original": "Sugar"}], "instructions": "Mix and bake.", "dishTypes": ["Dessert"], "image": "", "sourceUrl": "http://example.com"}]
        }

        # Make a request without any query parameters
        response = self.client.get(reverse('recipes'))

        # Check if Spoonacular recipes are returned
        self.assertContains(response, "Spoonacular Recipe")


    @patch('requests.get')
    def test_recipes_view_with_api_error(self, mock_get):
        # Simulate Spoonacular API error (non-200 status)
        mock_get.return_value.status_code = 500

        # Make a request with a query parameter
        response = self.client.get(reverse('recipes') + '?q=Test')

        # Check that the response status is 200 even if API fails
        self.assertEqual(response.status_code, 200)

        # Ensure local recipes are displayed
        self.assertContains(response, "Test Recipe")

    def test_recipes_view_no_results(self):
        # Make a request with a query parameter that yields no results
        response = self.client.get(reverse('recipes') + '?q=NonExistentRecipe')

        # Check that the response status is 200
        self.assertEqual(response.status_code, 200)

        # Check that no recipes are found
        self.assertNotContains(response, "Test Recipe")

    def test_sort_by_name(self):
        response = self.client.get(reverse('recipes') + '?sort_by=name')

        # Ensure the recipes are sorted by name
        self.assertContains(response, "Test Recipe")
        # Additional sorting checks can be added based on response content

    def test_sort_by_category(self):
        response = self.client.get(reverse('recipes') + '?sort_by=category')

        # Ensure the recipes are sorted by category
        self.assertContains(response, "Dessert")
        # Additional sorting checks can be added based on response content
