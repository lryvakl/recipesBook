from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Recipe


class UrlsTestCase(TestCase):

    def setUp(self):
        # Створення тестового користувача
        self.user = User.objects.create_user(username='testuser', password='password')

        # Створення тестового рецепту
        self.recipe = Recipe.objects.create(
            name="Test Recipe",
            ingredients="Eggs, Milk, Flour",
            instructions="Mix ingredients and bake.",
            category="Dessert",
            author=self.user
        )

        # Логін користувача
        self.client.login(username='testuser', password='password')

    def test_add_recipe_url(self):
        url = reverse('add_recipe')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_to_favorites_url(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('add_to_favorites', args=[self.recipe.id]))
        # Перевірка, чи є перенаправлення на логін
        self.assertEqual(response.status_code, 200)  # Перевірка на правильний статус, якщо не потребує логіну
        # або перевірка перенаправлення на сторінку логіну:
        # self.assertRedirects(response, '/login/', status_code=302, target_status_code=200)

    def test_add_to_want_to_cook_url(self):
        url = reverse('add_to_want_to_cook', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_recipe_url(self):
        url = reverse('delete_recipe', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_url(self):
        url = reverse('recipe_detail', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_remove_from_favorites_url(self):
        url = reverse('remove_from_favorites', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_remove_from_want_to_cook_url(self):
        url = reverse('remove_from_want_to_cook', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_recipes_url(self):
        url = reverse('search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_to_favorites_spoonacular_url(self):
        url = reverse('add_to_favorites_spoonacular', args=["crunchy-brussels-sprouts-side-dish"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_to_want_to_cook_spoonacular_url(self):
        url = reverse('add_to_want_to_cook_spoonacular', args=["crunchy-brussels-sprouts-side-dish"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_spoonacular_url(self):
        url = reverse('recipe_detail_spoonacular', args=["crunchy-brussels-sprouts-side-dish"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
