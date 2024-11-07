
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='mainPage'),
    path('about-us',views.recipes_view, name='about-us'),
    path('login',views.login),
    path('register',views.register),
    path('changePass',views.changePass),
    path('profile',views.profile),
    path('addRecipe', views.addRecipe, name='addRecipe'),
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('recipes/', views.recipes_view, name='recipes')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
