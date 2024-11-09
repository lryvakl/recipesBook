
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='mainPage'),
    path('about-us',views.about, name='about-us'),
    path('login',views.login),
    path('register',views.register),
    path('changePass',views.changePass),
    path('profile',views.profile),
    path('addRecipe', views.addRecipe, name='addRecipe'),
    path('add_recipe/', views.add_recipe, name='add_recipe'),
]
