from django.conf import settings
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from django.db.models import Max
from .models import Background, Trasa, Punkt
from .forms import TrasaForm, PunktForm, RejestracjaForm
from PIL import Image, ImageDraw
import os
from pathlib import Path


@login_required
def edytuj_trase(request, trasa_id):
    trasa = get_object_or_404(Trasa, pk=trasa_id)
    if trasa.uzytkownik != request.user:
        return redirect('mapy:lista_tras_uzytkownika')

    punkty = trasa.punkty.all().order_by('kolejnosc')
    image_width, image_height = None, None

    try:
        obrazek_tla = trasa.obraz_tla.obrazek
        if obrazek_tla and os.path.exists(obrazek_tla.path):
            with Image.open(obrazek_tla.path) as img:
                image_width, image_height = img.size
    except Exception as e:
        print(f"Nie udało się pobrać wymiarów obrazu tła dla trasy {trasa.id}: {e}")

    # obsługa POST
    if request.method == 'POST':
        if 'dodaj_punkt' in request.POST:
            punkt_form = PunktForm(request.POST, trasa=trasa)
            if punkt_form.is_valid():
                nowy_punkt = punkt_form.save(commit=False)
                nowy_punkt.trasa = trasa
                ostatnia_kolejnosc = punkty.aggregate(Max('kolejnosc'))['kolejnosc__max']
                nowy_punkt.kolejnosc = (ostatnia_kolejnosc or 0) + 1
                nowy_punkt.save()
                return redirect('mapy:edytuj_trase', trasa_id=trasa.pk)
    else:
        punkt_form = PunktForm()
    


    # zakres dla X i Y
    if image_width is not None:
        zakres_x = f"Zakres: 0 - {image_width - 1}"
        punkt_form.fields['x'].help_text = zakres_x
    if image_height is not None:
        zakres_y = f"Zakres: 0 - {image_height - 1}"
        punkt_form.fields['y'].help_text = zakres_y
    

    # generowanie obrazu z trasą
    generated_image_url = None
    obraz_wygenerowany = False
    try:
        oryginalny_obraz_path = trasa.obraz_tla.obrazek.path

        image = Image.open(oryginalny_obraz_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        promien_punktu = 5
        kolor_punktu = "red"
        kolor_linii = "blue"
        grubosc_linii = 3

        for punkt in punkty:
            x, y = punkt.x, punkt.y
            bbox = (x - promien_punktu, y - promien_punktu, x + promien_punktu, y + promien_punktu)
            draw.ellipse(bbox, fill=kolor_punktu, outline="black")

        if punkty.count() > 1:
            punkty_do_linii = [(p.x, p.y) for p in punkty]
            draw.line(punkty_do_linii, fill=kolor_linii, width=grubosc_linii)

        # zapisywanie zmodyfikowanego obrazu
        generated_dir = Path(settings.MEDIA_ROOT) / 'generated_routes'
        generated_dir.mkdir(parents=True, exist_ok=True)

        generated_filename = f"route_{trasa.id}.png"
        generated_image_path = generated_dir / generated_filename
        image.save(generated_image_path, "PNG")
        generated_image_url = f"{settings.MEDIA_URL}generated_routes/{generated_filename}"

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono oryginalnego pliku obrazu dla trasy {trasa.id}")
        pass
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd podczas generowania obrazu trasy: {e}")
        pass

    # aktualizacja form
    context = {
        'trasa': trasa,
        'punkty': punkty,
        'punkt_form': punkt_form,
        'display_image_url': generated_image_url if generated_image_url else trasa.obraz_tla.obrazek.url,
        'obraz_wygenerowany': generated_image_url is not None
    }
    return render(request, 'mapy/edytuj_trase.html', context)

@login_required
def lista_obrazow_tla(request):
    obrazy = Background.objects.all()
    return render(request, 'mapy/lista_obrazow.html', {'obrazy': obrazy})

@login_required
def stworz_trase(request, obraz_id):
    obraz_tla = get_object_or_404(Background, pk=obraz_id)
    if request.method == 'POST':
        form = TrasaForm(request.POST)
        if form.is_valid():
            nowa_trasa = form.save(commit=False)
            nowa_trasa.uzytkownik = request.user
            nowa_trasa.obraz_tla = obraz_tla
            nowa_trasa.save()
            return redirect('mapy:edytuj_trase', trasa_id=nowa_trasa.pk)
    else:
        form = TrasaForm()
    return render(request, 'mapy/stworz_trase.html', {'form': form, 'obraz_tla': obraz_tla})


@login_required
def usun_punkt(request, punkt_id):
    punkt = get_object_or_404(Punkt, pk=punkt_id)
    trasa = punkt.trasa

    if trasa.uzytkownik != request.user:
        return redirect('mapy:lista_obrazow_tla')

    if request.method == 'POST':
        punkt.delete()
        return redirect('mapy:edytuj_trase', trasa_id=trasa.pk)
    else:
        return redirect('mapy:edytuj_trase', trasa_id=trasa.pk)


@login_required
def lista_tras_uzytkownika(request):
    trasy = Trasa.objects.filter(uzytkownik=request.user).order_by('-data_modyfikacji')
    return render(request, 'mapy/lista_tras_uzytkownika.html', {'trasy': trasy})


def rejestracja(request):
    if request.method == 'POST':
        form = RejestracjaForm(request.POST)
        if form.is_valid():
            
            user = form.save()
            
            login(request, user)

            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = RejestracjaForm()

    return render(request, 'registration/register.html', {'form': form})