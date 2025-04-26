from django import forms
from .models import Trasa, Punkt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import os
from PIL import Image

class TrasaForm(forms.ModelForm):
    class Meta:
        model = Trasa
        fields = ['nazwa']

class PunktForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.trasa = kwargs.pop('trasa', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Punkt
        fields = ['x', 'y']
        widgets = {
            'x': forms.NumberInput(attrs={'step': '1', 'required': True}),
            'y': forms.NumberInput(attrs={'step': '1', 'required': True}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        x = cleaned_data.get("x")
        y = cleaned_data.get("y")

        if self.trasa and x is not None and y is not None:
            try:
                obrazek = self.trasa.obraz_tla.obrazek
                if not obrazek or not os.path.exists(obrazek.path):
                     raise forms.ValidationError(
                         "Nie można zweryfikować współrzędnych - brak pliku obrazu tła.",
                         code='no_image_file'
                     )

                # pobierz wymiary obrazu
                with Image.open(obrazek.path) as img:
                    width, height = img.size

                # walidacja zakresu (współrzędne od 0 do wymiar-1)
                if not (0 <= x < width):
                    self.add_error('x', forms.ValidationError(
                        f"Współrzędna X musi być w zakresie od 0 do {width - 1}.",
                        code='x_out_of_bounds'
                    ))
                if not (0 <= y < height):
                    self.add_error('y', forms.ValidationError(
                        f"Współrzędna Y musi być w zakresie od 0 do {height - 1}.",
                        code='y_out_of_bounds'
                    ))

            except FileNotFoundError:
                self.add_error(None, forms.ValidationError(
                     "Nie można otworzyć pliku obrazu tła do walidacji.",
                     code='image_open_error'
                 ))
            except Exception as e:
                print(f"Nieoczekiwany błąd podczas walidacji wymiarów obrazu: {e}")
                self.add_error(None, forms.ValidationError(
                    "Wystąpił błąd podczas walidacji współrzędnych względem obrazu.",
                    code='validation_error'
                ))

        return cleaned_data

class RejestracjaForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Wymagane. Podaj poprawny adres email.'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
