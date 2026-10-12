# Bulbapedia Scraper (wikiscraper)

A modular Python CLI tool for scraping, parsing, and analyzing text and tables from [Bulbapedia](https://bulbapedia.bulbagarden.net), along with language frequency analysis.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

*Key dependencies: `requests`, `beautifulsoup4`, `pandas`, `matplotlib`, `wordfreq`, `pytest`.*

## CLI Usage

Run commands using `python wiki_scraper.py <options>`:

### 1. First Paragraph Summary
Extracts clean introductory text:
```bash
python wiki_scraper.py --summary "Team Rocket"
```

### 2. Table Extraction & Value Count
Parses the $n$-th table, displays cell frequencies, and exports to `<phrase>.csv`:
```bash
python wiki_scraper.py --table "Type" --number 2 --first-row-is-header
```

### 3. Word Counting
Counts article words and updates `./word-counts.json`:
```bash
python wiki_scraper.py --count-words "Pikachu"
```

### 4. Frequency Analysis & Plotting
Compares stored words against standard English word frequencies:
```bash
# Sort by article frequency
python wiki_scraper.py --analyze-relative-word-frequency --mode article --count 10 --chart plot.png

# Sort by language frequency
python wiki_scraper.py --analyze-relative-word-frequency --mode language --count 10
```

### 5. Recursive Crawler
Follows internal `/wiki/` links up to depth $n$ with a $t$-second delay:
```bash
python wiki_scraper.py --auto-count-words "Kanto" --depth 2 --wait 1.0
```

## Testing (Offline)

All tests run locally using saved HTML fixtures without network access:

```bash
# Unit tests
pytest tests/

# Integration test
python wiki_scraper_integration_test.py
```

## Jupyter Notebook

The included `language_analysis.ipynb` evaluates the `lang_confidence_score` heuristic across English, German and Polish for $k \in \{10, 100, 1000\}$.

## License & Attribution

- Scraped Bulbapedia content is licensed under **CC BY-NC-SA 3.0**.
- *Output generated under CC BY-NC-SA based on articles from [Bulbapedia](https://bulbapedia.bulbagarden.net/).*