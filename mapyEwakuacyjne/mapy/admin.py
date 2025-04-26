from django.contrib import admin
from .models import Background

@admin.register(Background)
class TloAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'obrazek', 'data_dodania')
    search_fields = ('nazwa', 'opis')
    list_filter = ('data_dodania',)
