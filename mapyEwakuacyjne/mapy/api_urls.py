from django.urls import path, include
from rest_framework_nested import routers
from . import api_views
from . import views

router = routers.SimpleRouter()
router.register(r'trasy', api_views.TrasaViewSet, basename='trasa')

trasy_router = routers.NestedSimpleRouter(router, r'trasy', lookup='trasa')
trasy_router.register(r'punkty', api_views.PunktViewSet, basename='trasa-punkty')

urlpatterns = [
    path('obrazy/', views.lista_obrazow_tla, name='lista_obrazow_tla'),
    path('trasa/nowa/<int:obraz_id>/', views.stworz_trase, name='stworz_trase'),
    path('trasa/edytuj/<int:trasa_id>/', views.edytuj_trase, name='edytuj_trase'),
    path('punkt/usun/<int:punkt_id>/', views.usun_punkt, name='usun_punkt'),
    path('moje-trasy/', views.lista_tras_uzytkownika, name='lista_tras_uzytkownika'),
    path('', views.lista_obrazow_tla, name='index'),
    path('', include(router.urls)),
    path('', include(trasy_router.urls)),
]