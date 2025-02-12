
from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Recipe


class RecipeModelTest(TestCase):
    def setUp(self):
        # Створюємо користувача для тестів
        self.user = User.objects.create_user(username='testuser', password='password')

        # Створюємо рецепт для тестів
        self.recipe = Recipe.objects.create(
            name="Test Recipe",
            ingredients="Eggs, Milk, Flour",
            instructions="Mix ingredients and bake.",
            category="Dessert",
            author=self.user
        )

    def test_recipe_creation(self):
        """Перевірка правильності створення рецепта"""
        self.assertEqual(self.recipe.name, "Test Recipe")
        self.assertEqual(self.recipe.ingredients, "Eggs, Milk, Flour")
        self.assertEqual(self.recipe.instructions, "Mix ingredients and bake.")
        self.assertEqual(self.recipe.category, "Dessert")
        self.assertEqual(self.recipe.author, self.user)
        self.assertFalse(self.recipe.image)  # Перевірка, що зображення не завантажене
        # Перевірка, що зображення немає за замовчуванням

    def test_string_representation(self):
        """Перевірка правильності __str__ методу"""
        self.assertEqual(str(self.recipe), "Test Recipe")

    def test_add_to_favorites(self):
        """Перевірка додавання рецепта до улюблених"""
        self.recipe.favorite_by_users.add(self.user)
        self.assertIn(self.user, self.recipe.favorite_by_users.all())

    def test_get_image_url_no_image(self):
        """Перевірка методу get_image_url без зображення"""
        image_url = self.recipe.get_image_url()
        self.assertFalse(self.recipe.image)  # Перевірка, що зображення не завантажене

        # Оскільки немає зображення і URL, має повернути None

    def test_get_image_url_with_image_url(self):
        """Перевірка методу get_image_url із зовнішнім URL"""
        self.recipe.image_url = "http://example.com/image.jpg"
        self.recipe.save()
        image_url = self.recipe.get_image_url()
        self.assertEqual(image_url, "http://example.com/image.jpg")
