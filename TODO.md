# Plan Implementacji Edytora Plansz "Połącz Kropki"

## Kontekst i Cel

Celem jest stworzenie interfejsu do definiowania plansz do gry "Połącz Kropki". Użytkownik będzie mógł określić wymiary siatki, rozmieścić na niej pary kolorowych kropek i zapisać konfigurację. Ta plansza stanie się nowym rodzajem "tła" dla przyszłych interakcji.

## Faza 1: Backend - Modyfikacje Modeli Django

1.  **Nowy Model `GameBoard`**:
    * W pliku `mapy/models.py` utwórz nowy model, np. `GameBoard`.
    * Pola modelu:
        * `user`: `models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_boards')` - powiązanie z użytkownikiem.
        * `name`: `models.CharField(max_length=100, verbose_name="Nazwa planszy")` - nazwa planszy.
        * `rows`: `models.PositiveIntegerField(verbose_name="Liczba wierszy")` - wymiar planszy.
        * `cols`: `models.PositiveIntegerField(verbose_name="Liczba kolumn")` - wymiar planszy.
        * `dots_config`: `models.JSONField(default=list, blank=True, verbose_name="Konfiguracja kropek")` - do przechowywania informacji o kropkach. Będzie to lista słowników, np. `[{'row': r, 'col': c, 'color': '#RRGGBB', 'pair_id': 'unique_id_for_pair'}, ...]`. `pair_id` pomoże identyfikować kropki należące do tej samej pary.
        * `created_at`: `models.DateTimeField(auto_now_add=True)`
        * `updated_at`: `models.DateTimeField(auto_now=True)`
    * Dodaj metodę `__str__` dla czytelnej reprezentacji.
    * Zarejestruj model w `mapy/admin.py`, aby był widoczny w panelu admina (głównie do celów deweloperskich i podglądu).

2.  **Migracje**:
    * Po zdefiniowaniu modelu, wykonaj migracje:
        ```bash
        python manage.py makemigrations mapy
        python manage.py migrate
        ```

## Faza 2: Backend - Formularze Django

1.  **Formularz `GameBoardForm`**:
    * W pliku `mapy/forms.py` utwórz nowy formularz `GameBoardForm` dziedziczący z `forms.ModelForm`.
    * Pola: `name`, `rows`, `cols`.
    * `dots_config` będzie zarządzane przez TypeScript i wysyłane jako JSON, więc nie musi być bezpośrednio w formularzu HTML (chyba że jako ukryte pole do przekazania danych, ale preferowane jest wysłanie JSON przez Fetch API).

## Faza 3: Backend - Widoki i URL-e Django

1.  **URL-e (`mapy/urls.py`)**:
    * `/boards/`: Lista plansz użytkownika (GET).
    * `/boards/create/`: Tworzenie nowej planszy (GET - wyświetl formularz, POST - zapisz nową planszę).
    * `/boards/<int:board_id>/edit/`: Edycja istniejącej planszy (GET - wyświetl formularz z danymi, POST - zaktualizuj planszę).
    * `/boards/<int:board_id>/delete/`: Usuwanie planszy (POST).
    * `/api/boards/<int:board_id>/save_config/`: Endpoint API do zapisywania/aktualizacji konfiguracji kropek z frontendu (POST/PUT, przyjmujący JSON).

2.  **Widoki (`mapy/views.py`)**:

    * **`game_board_list_view(request)`**:
        * Wymaga zalogowania (`@login_required`).
        * Pobiera plansze (`GameBoard.objects.filter(user=request.user)`).
        * Renderuje szablon z listą plansz.

    * **`game_board_create_view(request)`**:
        * Wymaga zalogowania.
        * **GET**: Tworzy instancję `GameBoardForm`, renderuje szablon do tworzenia planszy (z formularzem nazwy i wymiarów oraz kontenerem na siatkę).
        * **POST**: (Ten widok może obsługiwać tylko wstępne utworzenie planszy z nazwą i wymiarami, a kropki będą zapisywane przez dedykowany endpoint API. Alternatywnie, może przyjmować wstępną konfigurację, jeśli to upraszcza logikę).
            * Waliduje `GameBoardForm`.
            * Jeśli poprawny, tworzy nowy obiekt `GameBoard` (na razie bez kropek lub z pustą listą kropek).
            * Przekierowuje do widoku edycji tej nowej planszy.

    * **`game_board_edit_view(request, board_id)`**:
        * Wymaga zalogowania.
        * Pobiera `GameBoard` o danym `board_id`, upewniając się, że należy do `request.user`.
        * **GET**: Tworzy instancję `GameBoardForm` z danymi planszy. Renderuje szablon edycji, przekazując dane planszy (w tym `dots_config` jako JSON do wykorzystania przez TypeScript) do szablonu.
        * **POST**: (Obsługa zmiany nazwy/wymiarów przez standardowy formularz Django).
            * Waliduje `GameBoardForm`.
            * Aktualizuje obiekt `GameBoard`.
            * Renderuje ten sam szablon z potwierdzeniem lub błędami.

    * **`game_board_delete_view(request, board_id)`**:
        * Wymaga zalogowania.
        * Pobiera `GameBoard`, upewniając się, że należy do `request.user`.
        * Obsługuje żądanie POST do usunięcia planszy.
        * Przekierowuje do listy plansz.

    * **`save_board_config_api_view(request, board_id)`**:
        * Wymaga zalogowania.
        * Przyjmuje żądania POST/PUT (dla aktualizacji).
        * Oczekuje danych JSON w ciele żądania (`request.body`) zawierających `rows`, `cols` (opcjonalnie, jeśli można zmieniać) i `dots_config`.
        * Pobiera `GameBoard` o danym `board_id` (sprawdza właściciela).
        * Waliduje otrzymane dane.
        * Aktualizuje pola `rows`, `cols` (jeśli są przesyłane) i `dots_config` na obiekcie `GameBoard`.
        * Zapisuje zmiany.
        * Zwraca odpowiedź JSON (np. `{'status': 'success'}` lub `{'status': 'error', 'errors': ...}`). Pamiętaj o `JsonResponse`.
        * Zabezpiecz ten widok przed CSRF, jeśli nie używasz DRF (Django REST Framework) – np. przez `ensure_csrf_cookie` na widoku GET i poprawne wysyłanie tokena z frontendu.

## Faza 4: Frontend - Szablony HTML

1.  **`lista_plansz.html` (Nowy szablon)**:
    * Wyświetla tabelę/listę plansz użytkownika z linkami do edycji i przyciskami usuwania.
    * Link do tworzenia nowej planszy.

2.  **`tworzenie_edycja_planszy.html` (Nowy szablon)**:
    * Zawiera formularz Django dla nazwy, wierszy i kolumn (wyrenderowany przez `{{ form.as_p }}`).
    * Kontener `div` z unikalnym `id` (np. `id="grid-container"`), w którym TypeScript wygeneruje siatkę.
    * Elementy interfejsu do wyboru koloru (np. `div`y z predefiniowanymi kolorami, które będą klikalne).
    * Przycisk "Zapisz konfigurację planszy" (`<button type="button" id="save-board-button">Zapisz planszę</button>`). Zwróć uwagę na `type="button"`, aby nie wysyłał formularza HTML.
    * Ukryte pole lub zmienna JavaScript do przechowywania `board_id` (jeśli edytujemy istniejącą planszę).
    * Miejsce na wyświetlanie komunikatów (np. o sukcesie zapisu, błędach).
    * Link do powrotu do listy plansz.
    * Tag `<script type="module" src="{% static 'mapy/js/dist/board_editor.js' %}"></script>` (nowy plik TS/JS dla tej funkcjonalności).

## Faza 5: Frontend - Logika TypeScript (np. `mapy/typescript/board_editor.ts`)

1.  **Struktura Danych i Stanu**:
    * Zdefiniuj interfejsy dla kropki (`Dot { row: number; col: number; color: string; pair_id: string; }`) i stanu planszy (`BoardState { rows: number; cols: number; dots: Dot[]; }`).
    * Zmienne do przechowywania aktualnie wybranego koloru, aktualnie umieszczanej pary (czy to pierwsza, czy druga kropka z pary), ID dla par.

2.  **Inicjalizacja**:
    * Pobierz referencje do elementów DOM (kontener siatki, pola input wymiarów, paleta kolorów, przycisk zapisu).
    * Jeśli edytujemy istniejącą planszę, wczytaj jej dane (wymiary, `dots_config`) przekazane z szablonu Django (np. z atrybutu `data-*` na kontenerze lub ze zmiennej JS).
    * Dodaj listenery do pól wymiarów (aby regenerować siatkę) lub do przycisku "Generuj siatkę".
    * Dodaj listenery do palety kolorów.
    * Dodaj listener do przycisku "Zapisz".

3.  **Generowanie Siatki (`generateGrid(rows, cols)` )**:
    * Czyści poprzednią zawartość `grid-container`.
    * Tworzy dynamicznie elementy `div` (lub `td` jeśli używasz tabeli) dla każdej komórki.
    * Nadaje każdej komórce atrybuty `data-row` i `data-col`.
    * Dodaje do każdej komórki event listener `click`.
    * Stylizuje siatkę za pomocą CSS (np. CSS Grid).

4.  **Wybór Koloru**:
    * Po kliknięciu na element palety, ustaw wybrany kolor w stanie TS.
    * Wizualnie zaznacz aktywny kolor w palecie.
    * Resetuj stan umieszczania pary (oczekuj na pierwszą kropkę nowej pary).

5.  **Obsługa Kliknięcia na Komórkę Siatki (`handleCellClick(row, col, cellElement)`)**:
    * Sprawdź, czy wybrano kolor.
    * Sprawdź, czy komórka jest pusta (na podstawie stanu TS).
    * **Logika umieszczania pary**:
        * Jeśli to pierwsza kropka dla danego koloru/pary:
            * Zapisz ją w stanie TS (z nowym `pair_id`).
            * Wizualizuj kropkę na siatce (zmień tło komórki, dodaj element).
            * Ustaw stan, że oczekujesz na drugą kropkę tej pary.
        * Jeśli to druga kropka dla tej samej pary:
            * Upewnij się, że to inna komórka.
            * Zapisz ją w stanie TS (z tym samym `pair_id`).
            * Wizualizuj.
            * Zresetuj stan umieszczania pary dla tego koloru (lub oznacz kolor jako "zużyty" dla tej pary).
    * Obsługa błędów (np. próba postawienia na zajętym polu, próba postawienia trzeciej kropki tego samego koloru).

6.  **Wizualizacja Kropek (`renderDots()`)**:
    * Funkcja, która na podstawie stanu `BoardState.dots` aktualizuje wygląd siatki, rysując wszystkie umieszczone kropki. Wywoływana po każdej zmianie.

7.  **Zbieranie Danych do Zapisu (`getBoardDataForSave()`)**:
    * Pobiera nazwę planszy z formularza HTML.
    * Pobiera aktualne wymiary (`rows`, `cols`) ze stanu TS (lub z pól input).
    * Pobiera listę kropek (`dots`) ze stanu TS.
    * Zwraca obiekt gotowy do wysłania jako JSON.

8.  **Zapis Planszy (`saveBoard()`)**:
    * Wywołuje `getBoardDataForSave()`.
    * Używa `fetch` API do wysłania żądania POST/PUT do odpowiedniego endpointu Django (`/api/boards/<board_id>/save_config/` lub endpoint tworzenia, jeśli to nowa plansza).
    * Dołącza token CSRF do nagłówków żądania. Sposób pobrania tokena CSRF:
        ```typescript
        function getCookie(name: string): string | null {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const csrfToken = getCookie('csrftoken');
        // W fetch: headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' }
        ```
    * Obsługuje odpowiedź serwera (sukces, błędy walidacji).

9.  **(Opcjonalnie) Edycja/Usuwanie Kropek**:
    * Dodaj mechanizm usuwania umieszczonych kropek (np. ponowne kliknięcie na kropkę, przycisk "Usuń ostatnią parę").

## Faza 6: Style CSS

* Style dla siatki (komórki, obramowania).
* Style dla palety kolorów.
* Style dla umieszczonych kropek (różne kolory).
* Style dla podświetleń, aktywnych elementów.

## Faza 7: Testowanie i Iteracje

* Dokładne testowanie wszystkich funkcjonalności: tworzenie siatki, wybór koloru, umieszczanie par kropek, walidacja, zapis, ładowanie, edycja, usuwanie.
* Testowanie responsywności (jeśli dotyczy).
* Debugowanie z użyciem narzędzi deweloperskich przeglądarki.

Ten plan jest dość obszerny. Zalecam implementację krok po kroku, zaczynając od modeli Django, następnie podstawowych widoków i szablonów, a potem przechodząc do logiki TypeScript dla generowania siatki i stopniowo dodając kolejne interakcje.
