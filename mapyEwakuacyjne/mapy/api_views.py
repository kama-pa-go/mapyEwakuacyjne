from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Trasa, Punkt
from .serializers import TrasaSerializer, PunktSerializer
from .permissions import IsOwnerOrReadOnly

class TrasaViewSet(viewsets.ModelViewSet):
    """
    API endpoint do zarządzania trasami.
    """
    serializer_class = TrasaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Zwraca trasy należące do zalogowanego użytkownika lub wszystkie, jeśli jest to admin.
        Dla niezalogowanych zwróci wszystkie (ze względu na IsAuthenticatedOrReadOnly).
        Można to dostosować wg potrzeb.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return Trasa.objects.all()
            return Trasa.objects.filter(uzytkownik=user)
        return Trasa.objects.all()


    def perform_create(self, serializer):
        """
        Przypisuje zalogowanego użytkownika jako właściciela nowo tworzonej trasy.
        """
        serializer.save(uzytkownik=self.request.user)

class PunktViewSet(viewsets.ModelViewSet):
    """
    API endpoint do zarządzania punktami konkretnej trasy.
    """
    serializer_class = PunktSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Zwraca tylko punkty należące do trasy określonej w URL.
        """
        trasa_pk = self.kwargs['trasa_pk'] 
        trasa = get_object_or_404(Trasa, pk=trasa_pk)

        return Punkt.objects.filter(trasa=trasa)

    def perform_create(self, serializer):
        """
        Przypisuje punkt do trasy z URL i sprawdza, czy użytkownik jest jej właścicielem.
        """
        trasa_pk = self.kwargs['trasa_pk']
        trasa = get_object_or_404(Trasa, pk=trasa_pk)

        if trasa.uzytkownik != self.request.user:
            raise PermissionDenied("Nie możesz dodawać punktów do trasy, której nie jesteś właścicielem.")

        serializer.save(trasa=trasa)