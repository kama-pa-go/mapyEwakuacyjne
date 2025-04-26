from django.db import models
from django.conf import settings
import os


class Background(models.Model):
    nazwa = models.CharField(max_length=100)
    opis = models.TextField(blank=True)
    data_dodania = models.DateTimeField(auto_now_add=True)
    obrazek = models.ImageField(
        upload_to='obrazki/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nazwa

class Trasa(models.Model):
    nazwa = models.CharField(max_length=200, verbose_name="Nazwa trasy")

    uzytkownik = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trasy',
        verbose_name="Użytkownik"
    )
    
    obraz_tla = models.ForeignKey(
        Background,
        on_delete=models.CASCADE,
        related_name='trasy',
        verbose_name="Obraz tła"
    )
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    data_modyfikacji = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"'{self.nazwa}' na '{self.obraz_tla.nazwa}' (użytkownik: {self.uzytkownik.username})"

    class Meta:
        verbose_name = "Trasa"
        verbose_name_plural = "Trasy"
        ordering = ['-data_modyfikacji']


class Punkt(models.Model):
    trasa = models.ForeignKey(
        Trasa,
        on_delete=models.CASCADE,
        related_name='punkty',
        verbose_name="Trasa"
    )
    x = models.IntegerField(verbose_name="Współrzędna X")
    y = models.IntegerField(verbose_name="Współrzędna Y")
    kolejnosc = models.PositiveIntegerField(default=0, verbose_name="Kolejność")
    data_dodania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Punkt ({self.x}, {self.y}) [Trasa: {self.trasa.nazwa}]"

    class Meta:
        verbose_name = "Punkt"
        verbose_name_plural = "Punkty"
        # sortowanie punktów w ramach trasy
        ordering = ['trasa', 'kolejnosc', 'data_dodania']