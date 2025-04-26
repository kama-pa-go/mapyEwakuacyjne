# MapyEwakuacyjne
Django aplication for WWW Aplications (project no 3)

Django z domieszką Tailwinda. 
Żeby odpalić projekt u siebie na komputerze trzeba mieć zainstalowane następujące komponenty do Django:
- Pillow do obsługi ImageField (obsługa obrazów)
- django-tailwind-cli (tailwind)

- drf-nested-routers (API)
- djangorestframework (API)
- drf-yasg (API)

podczas poprawnej instalacji modułu dijango_tailwind_cli w folderze głównym projektu powinien pojawić się jeszcze ukryty katalog .django_tailwind_cli wraz z plikami:
  - source.css
  - tailwindcss-windows-x64-4.1.4 (przynajmiej w środowisku windowsa)

aby odpalić testy należy w głównym katalogo (czyli MapyEwakuacyjne) puścić z terminala:
  py manage.py test
  w razie czego dowód, że w moim środowisku działa:
  ![image](https://github.com/user-attachments/assets/217cb33f-51e5-499b-ba38-c5ba28cde50d)

Źródła:
  formularze uywane do rejestracji pochodzą w większości z: https://github.com/macdhuibh/django-registration-templates

