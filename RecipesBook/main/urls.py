
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import RegisterView
from django.contrib.auth.views import LoginView
from .forms import UsernameOrEmailAuthenticationForm

urlpatterns = [

    path('', views.main_page, name='mainPage'),
    path('about-us/',views.recipes_view, name='about-us'),
    path('login/', LoginView.as_view(authentication_form=UsernameOrEmailAuthenticationForm),name='login'),
    path('register/',RegisterView.as_view(), name='register'),
    path('changePass/',views.changePass, name='changePass'),
    path('profile/',views.profile, name='profile'),
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('recipes/', views.recipes_view, name='recipes'),
    path('about-us', views.search_recipes, name='search'),
    path('search/', views.search_ingredients, name='search_ingredients'),
    path('recipe-detail/<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe_detail_spoonacular/<str:title>/', views.recipe_detail_spoonacular, name='recipe_detail_spoonacular'),
    path('add-to-favorites/<int:id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('add-to-favorites-spoonacular/<str:title>/', views.add_to_favorites_spoonacular, name='add_to_favorites_spoonacular'),
    path('delete-recipe/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    path('add-to-want-to-cook/<int:recipe_id>/', views.add_to_want_to_cook, name='add_to_want_to_cook'),
    path('add-to-want-to-cook-spoonacular/<str:title>/', views.add_to_want_to_cook_spoonacular, name='add_to_want_to_cook_spoonacular'),
    path('remove_from_want_to_cook/<int:recipe_id>', views.remove_from_want_to_cook, name='remove_from_want_to_cook'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

