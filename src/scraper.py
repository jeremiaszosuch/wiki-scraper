import os
import string
import time
from collections import Counter
import requests
from bs4 import BeautifulSoup


class WikiScraper:
    def __init__(self, base_url: str, use_local: bool = False) -> None:
        self.base_url = base_url
        self.use_local = use_local
        self.data_dir = "data"

    def _get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": (
                "WikiScraperStudentProject/1.0 "
                "(educational use; jo469488@students.mimuw.edu.pl)"
            )
        }

    def _get_soup(self, phrase: str) -> BeautifulSoup:
        # Normalize the phrase
        safe_phrase = phrase.strip().replace(" ", "_")

        # Get content from the local file
        if self.use_local:
            file_path = os.path.join(self.data_dir, f"{safe_phrase}.html")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    return BeautifulSoup(file, "html.parser")
            else:
                raise FileNotFoundError(f"File not found: '{file_path}'")

        # Prepare the url and get content from the site
        url = f"{self.base_url}/wiki/{safe_phrase}"
        response = requests.get(url, headers=self._get_headers(), timeout=5)
        response.raise_for_status()

        return BeautifulSoup(response.text, "html.parser")

    def _get_valid_links(self, soup: BeautifulSoup) -> list[str]:
        # Find the main article block
        content = soup.select_one("#mw-content-text .mw-parser-output")
        if not content:
            return []

        # Search for all the links with /wiki/ prefix
        raw_links = content.select("p a, ul a, ol a")

        # Extract the phrases, normalize, check and add them to the list
        links = []
        for link in raw_links:
            href = link.get("href")

            if not href:
                continue
            if "/wiki/" not in href:
                continue
            if href.startswith("http"):
                if self.base_url not in href:
                    continue

            phrase = href.split("/wiki/")[-1]
            if ":" not in phrase and "#" not in phrase:
                links.append(phrase)

        return links

    def get_summary(self, phrase: str) -> str:
        # Fetch site content
        soup = self._get_soup(phrase)

        # Find the main article block
        content = soup.select_one("#mw-content-text .mw-parser-output")
        if not content:
            raise ValueError("Article content block not found")

        # Get all the paragraphs and find the first one with text
        paragraphs = content.find_all("p", recursive=False)
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                return text

        raise ValueError("No text paragraph found in the article")

    def get_table(self, phrase: str, table_number: int) -> list[list[str]]:
        # Fetch site content
        soup = self._get_soup(phrase)

        # Find the table
        tables = soup.find_all("table")
        idx = table_number - 1
        if idx < 0 or idx >= len(tables):
            raise ValueError(
                f"Table #{table_number} not found. "
                f"Article has {len(tables)} tables."
            )
        target = tables[idx]

        # Extract data from the table
        data = []
        rows = target.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:
                data.append(row_data)

        return data

    def count_words(self, phrase: str) -> dict[str, int]:
        # Fetch site content
        soup = self._get_soup(phrase)

        # Find the main article block
        content = soup.select_one("#mw-content-text .mw-parser-output")
        if not content:
            raise ValueError("Article content block not found")

        # Get all the text from paragraphs
        text = ""
        paragraphs = content.find_all("p")
        for p in paragraphs:
            text += p.get_text() + " "

        # Seperate words, remove punctuation and normalize
        words = text.lower().split()
        clean_words = []
        translator = str.maketrans("", "", string.punctuation)
        for word in words:
            stripped_word = word.translate(translator)
            if len(stripped_word) > 1:
                clean_words.append(stripped_word)

        # Count words
        return dict(Counter(clean_words))

    def auto_count_words(self, start_phrase: str, depth: int,
                         wait: float) -> dict[str, dict[str, int]]:
        results = {}
        visited = set()
        queue = [(start_phrase, 0)]

        # Crawl until the are no more sites to visit (until set depth)
        while queue:
            current_phrase, current_depth = queue.pop(0)

            # Skip if already visited, else mark as visited
            if current_phrase in visited:
                continue
            visited.add(current_phrase)

            try:
                # Count words in the article
                results[current_phrase] = self.count_words(current_phrase)

                if current_depth < depth:
                    # Fetch site content and get all links
                    soup = self._get_soup(current_phrase)
                    new_links = self._get_valid_links(soup)

                    # Add all unvisited links to the queue
                    for link in new_links:
                        if link not in visited:
                            queue.append((link, current_depth + 1))

                # Wait set amount of seconds
                if queue:
                    time.sleep(wait)

            # Continue crawling despite an error on one of the sites
            except (requests.exceptions.RequestException, ValueError,
                    AttributeError, FileNotFoundError):
                continue

        return results
