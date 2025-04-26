import os
from pathlib import Path
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile 

from .models import Trasa, Punkt, Background


# --- testy modeli ---
class ModelTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password123')
        base_dir = Path(__file__).resolve().parent.parent.parent
        image_path = base_dir / 'mapyEwakuacyjne' / 'media' / 'obrazki' / 'bardzoStaryPlan.jpeg' # "C:\Users\user\mapyEwakuacyjne\media\obrazki\bardzoStaryPlan.jpeg"

        if not image_path.is_file():
             raise FileNotFoundError(f"Nie znaleziono pliku obrazu testowego w: {image_path}")
        with open(image_path, 'rb') as f:
            image_content = f.read()

        uploaded_image = SimpleUploadedFile(
            name='tlo_testowe.jpg',
            content=image_content,
            content_type='image/jpeg'
        )

        cls.test_tlo = Background.objects.create(
            nazwa='Tlo Testowe z Pliku',
            opis='Opis testowego obrazu tła',
            obrazek=uploaded_image
        )

        cls.trasa = Trasa.objects.create(
            nazwa='Testowa Trasa Model',
            uzytkownik=cls.user,
            obraz_tla=cls.test_tlo
        )

    def test_tworzenie_trasy(self):
        """sprawdza, czy trasa została poprawnie stworzona i zapisana."""
        self.assertEqual(self.trasa.nazwa, 'Testowa Trasa Model')
        self.assertEqual(self.trasa.uzytkownik.username, 'testuser')
        # self.assertEqual(str(self.trasa), 'Testowa Trasa Model')

    def test_tworzenie_punktu_trasy(self):
        """sprawdza tworzenie punktu i relację z trasą."""
        punkt = Punkt.objects.create(
            trasa=self.trasa,
            kolejnosc=1,
            x=52.2297,
            y=21.0122
        )
        self.assertEqual(punkt.kolejnosc, 1)
        self.assertEqual(punkt.trasa, self.trasa)
        self.assertEqual(self.trasa.punkty.count(), 1)
        self.assertEqual(self.trasa.punkty.first(), punkt)


# --- testy widoków---
class WebViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1', password='password123')
        cls.user2 = User.objects.create_user(username='user2', password='password123')

        base_dir = Path(__file__).resolve().parent.parent.parent
        image_path = base_dir / 'mapyEwakuacyjne' / 'media' / 'obrazki' / 'bardzoStaryPlan.jpeg'
        if not image_path.is_file():
            raise FileNotFoundError(f"Nie znaleziono pliku obrazu testowego w: {image_path}")
        with open(image_path, 'rb') as f:
            image_content = f.read()
        uploaded_image = SimpleUploadedFile(name='tlo_web.jpg', content=image_content, content_type='image/jpeg')

        cls.test_obraz_tla_web = Background.objects.create(nazwa='Tlo Web z Pliku', obrazek=uploaded_image)
        cls.trasa_user1 = Trasa.objects.create(nazwa='Trasa Usera 1', uzytkownik=cls.user1, obraz_tla=cls.test_obraz_tla_web)
        cls.trasa_user2 = Trasa.objects.create(nazwa='Trasa Usera 2', uzytkownik=cls.user2, obraz_tla=cls.test_obraz_tla_web)
        cls.url_listy_tras = reverse('lista_tras_uzytkownika')
        cls.url_logowania = reverse('login')
        cls.url_dodaj_punkt = reverse('edytuj_trase', args=[cls.trasa_user1.id])

    def setUp(self):
        self.client = Client()

    def test_dostep_do_listy_tras_wymaga_logowania(self):
        """sprawdza przekierowanie do logowania dla niezalogowanego użytkownika."""
        response = self.client.get(self.url_listy_tras)
        self.assertRedirects(response, f'{self.url_logowania}?next={self.url_listy_tras}')

    def test_zalogowany_uzytkownik_widzi_liste_tras(self):
        """sprawdza dostęp do listy tras po zalogowaniu."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.url_listy_tras)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mapy/lista_tras_uzytkownika.html') 

    def test_uzytkownik_widzi_tylko_swoje_trasy(self):
        """sprawdza, czy na liście tras użytkownik widzi tylko swoje trasy."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.url_listy_tras)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.trasa_user1.nazwa)
        self.assertNotContains(response, self.trasa_user2.nazwa)


# --- testy API REST ---

class APITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='apiuser1', password='password123')
        cls.user2 = User.objects.create_user(username='apiuser2', password='password123')
        cls.token1 = Token.objects.create(user=cls.user1)
        cls.token2 = Token.objects.create(user=cls.user2)

        base_dir = Path(__file__).resolve().parent.parent
        image_path = base_dir / 'media' / 'obrazki' / 'bardzoStaryPlan.jpeg'
        if not image_path.is_file():
            raise FileNotFoundError(f"Nie znaleziono pliku obrazu testowego w: {image_path}")
        with open(image_path, 'rb') as f:
            image_content = f.read()
        uploaded_image = SimpleUploadedFile(name='tlo_api.png', content=image_content, content_type='image/png')

        cls.test_obraz_tla_api = Background.objects.create(nazwa='Tlo API z Pliku', obrazek=uploaded_image)


        cls.trasa_user1 = Trasa.objects.create(nazwa='Trasa API Usera 1', uzytkownik=cls.user1, obraz_tla=cls.test_obraz_tla_api)
        cls.punkt_user1 = Punkt.objects.create(trasa=cls.trasa_user1, x=1.0, y=1.0)
        cls.trasa_user2 = Trasa.objects.create(nazwa='Trasa API Usera 2', uzytkownik=cls.user2, obraz_tla=cls.test_obraz_tla_api)

        cls.url_trasy_list = reverse('trasa-list')
        cls.url_trasa_detail = reverse('trasa-detail', args=[cls.trasa_user1.id])
        cls.url_punkty_list = reverse('trasa-punkty-list', args=[cls.trasa_user1.id])
        cls.url_punkt_detail = reverse('trasa-punkty-detail', args=[cls.trasa_user1.id, cls.punkt_user1.id])

    def setUp(self):
        pass

    def test_api_dostep_bez_tokena(self):
        """sprawdza, czy żądanie POST do API bez tokena jest odrzucane (401)."""
        response = self.client.post(self.url_trasy_list, {'nazwa': 'Nowa Trasa Bez Tokena'})
        self.assertEqual(response.status_code, 401)

    def test_api_uzytkownik_nie_widzi_cudzej_trasy(self):
        """sprawdza, czy użytkownik 2 nie ma dostępu do szczegółów trasy użytkownika 1 (404 lub 403)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        url_cudzej_trasy = reverse('trasa-detail', args=[self.trasa_user1.id])
        response = self.client.get(url_cudzej_trasy)
        self.assertIn(response.status_code, [403, 404])

    def test_api_uzytkownik_nie_moze_usunac_cudzej_trasy(self):
        """sprawdza, czy użytkownik 2 nie może usunąć trasy użytkownika 1 (403 lub 404)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        url_cudzej_trasy = reverse('trasa-detail', args=[self.trasa_user1.id])
        response = self.client.delete(url_cudzej_trasy)
        self.assertIn(response.status_code, [403, 404])
        self.assertTrue(Trasa.objects.filter(id=self.trasa_user1.id).exists())


    def test_api_pobranie_listy_tras_uzytkownika(self):
        """sprawdza, czy GET /api/trasy/ zwraca tylko trasy zalogowanego użytkownika."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.get(self.url_trasy_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nazwa'], self.trasa_user1.nazwa)

    def test_api_tworzenie_trasy(self):
        """sprawdza tworzenie nowej trasy przez POST /api/trasy/."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        trasy_przed = Trasa.objects.filter(uzytkownik=self.user1).count()
        dane_post = {'nazwa': 'Nowa Trasa z API', 'obraz_tla': self.test_obraz_tla_api.id}
        response = self.client.post(self.url_trasy_list, dane_post, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['nazwa'], 'Nowa Trasa z API')
        self.assertEqual(response.data['uzytkownik'], self.user1.username)
        trasy_po = Trasa.objects.filter(uzytkownik=self.user1).count()
        self.assertEqual(trasy_po, trasy_przed + 1)

    def test_api_dodawanie_punktu_do_trasy(self):
        """sprawdza dodawanie punktu przez POST /api/trasy/{id}/punkty/."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        punkty_przed = Punkt.objects.filter(trasa=self.trasa_user1).count()
        dane_post = {
            'kolejnosc': 1,
            'x': 52,
            'y': 215
        }
        url_dodaj_punkt = reverse('trasa-punkty-list', args=[self.trasa_user1.id])
        response = self.client.post(url_dodaj_punkt, dane_post, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['trasa'], self.trasa_user1.id)
        punkty_po = Punkt.objects.filter(trasa=self.trasa_user1).count()
        self.assertEqual(punkty_po, punkty_przed + 1)

    def test_api_usuniecie_punktu(self):
        """sprawdza usuwanie punktu przez DELETE /api/trasy/{id}/punkty/{pid}/."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        punkty_przed = Punkt.objects.filter(trasa=self.trasa_user1).count()
        url_usun_punkt = reverse('trasa-punkty-detail', args=[self.trasa_user1.id, self.punkt_user1.id])
        response = self.client.delete(url_usun_punkt)
        self.assertEqual(response.status_code, 204)
        punkty_po = Punkt.objects.filter(trasa=self.trasa_user1).count()
        self.assertEqual(punkty_po, punkty_przed - 1)
        self.assertFalse(Punkt.objects.filter(id=self.punkt_user1.id).exists())

