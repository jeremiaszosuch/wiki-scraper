# WikiScraper

Profesjonalne narzędzie CLI do pobierania, analizowania i wizualizacji danych z serwisów opartych na silniku MediaWiki (np. Bulbapedia).

## 🚀 Możliwości

* **Pobieranie Tabel:** Ekstrakcja tabel ze stron Wiki i zapis do formatu CSV (z użyciem silnika `bs4`).
* **Analiza Tekstu:** Zliczanie częstości występowania słów w artykułach.
* **Analiza Relatywna:** Porównanie słownictwa w artykule vs. język ogólny.
* **Wizualizacja:** Generowanie wykresów porównawczych (`matplotlib`).
* **Crawler:** Rekurencyjne przeszukiwanie linków z opcją limitowania głębokości (`--depth`) i opóźnienia (`--wait`), aby uniknąć blokady.

## 🛠️ Instalacja

1.  **Sklonuj repozytorium:**
    ```bash
    git clone [https://github.com/JeremiSho/wiki-scraper.git](https://github.com/JeremiSho/wiki-scraper.git)
    cd wiki-scraper
    ```

2.  **Zainstaluj wymagane biblioteki:**
    Projekt wymaga kilku kluczowych bibliotek do poprawnego działania.
    ```bash
    pip install -r requirements.txt
    ```

## 📖 Użycie

Aplikację uruchamiamy z wiersza poleceń za pomocą polecenia:

```bash
python wiki_scraper.py <argumenty>
```

Pełną listę opcji uruchamiania można sprawdzić wywołując komendę z flagą `--help`.