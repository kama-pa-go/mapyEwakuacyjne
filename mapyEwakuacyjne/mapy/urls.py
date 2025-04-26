from django.urls import path, include
from . import views


app_name = "mapy"
urlpatterns = [
    path('obrazy/', views.lista_obrazow_tla, name='lista_obrazow_tla'),
    path('trasa/nowa/<int:obraz_id>/', views.stworz_trase, name='stworz_trase'),
    path('trasa/edytuj/<int:trasa_id>/', views.edytuj_trase, name='edytuj_trase'),
    path('punkt/usun/<int:punkt_id>/', views.usun_punkt, name='usun_punkt'),
    path('moje-trasy/', views.lista_tras_uzytkownika, name='lista_tras_uzytkownika'),
    path('', views.lista_obrazow_tla, name='index'),
]