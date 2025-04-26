from rest_framework import serializers
from .models import Trasa, Punkt
from django.contrib.auth.models import User

class PunktSerializer(serializers.ModelSerializer):
    class Meta:
        model = Punkt
        fields = ['id', 'trasa', 'x', 'y', 'kolejnosc', 'data_dodania']
        read_only_fields = ['trasa']

class TrasaSerializer(serializers.ModelSerializer):
    punkty = PunktSerializer(many=True, read_only=True)
    uzytkownik = serializers.ReadOnlyField(source='uzytkownik.username')

    class Meta:
        model = Trasa
        fields = ['id', 'nazwa', 'uzytkownik', 'obraz_tla', 'data_utworzenia', 'data_modyfikacji', 'punkty']
        read_only_fields = ['uzytkownik']