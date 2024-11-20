
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='mainPage'),
    path('about-us/',views.recipes_view, name='about-us'),
    path('login/',views.login, name='login'),
    path('register/',views.register, name='register'),
    path('changePass/',views.changePass, name='changePass'),
    path('profile/',views.profile, name='profile'),
    path('addRecipe/', views.addRecipe, name='addRecipe'),
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('recipes/', views.recipes_view, name='recipes'),
    path('about-us', views.search_recipes, name='search'),
    path('search/', views.search_ingredients, name='search_ingredients'),
    path('recipe-detail/<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe_detail_spoonacular/<str:title>/', views.recipe_detail_spoonacular, name='recipe_detail_spoonacular'),
    path('add-to-favorites/<int:id>/', views.add_to_favorites, name='add_to_favorites'),
    path('add_to_favorites_spoonacular/<slug:slug>/', views.add_to_favorites_spoonacular,name='add_to_favorites_spoonacular'),
    path('remove_from_favorites/<int:id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('add-to-favorites-spoonacular/<str:title>/', views.add_to_favorites_spoonacular, name='add_to_favorites_spoonacular'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

