"""
Scraping Module.

This module handles all network interactions, HTML parsing and data
extraction from the Wiki. It includes functionality for caching pages
locally and cleaning text data.
"""

import os
import string
from io import StringIO
from urllib.parse import unquote
from collections import Counter
import pandas as pd
import requests
from bs4 import BeautifulSoup


class WikiScraper:
    """A class responsible for fetching and parsing Wiki pages."""

    def __init__(self, base_url: str, use_local: bool = False,
                 cache_files: bool = False) -> None:
        """
        Initialize the scraper.

        Args:
            base_url (str): The root URL of the Wiki.
            use_local (bool): If True, fetch pages from local
                'data' directory.
            cache_files (bool): If True, save fetched pages to
                'data' directory.
        """
        self.base_url = base_url
        self.use_local = use_local
        self.cache_files = cache_files
        self.data_dir = "data"
        self.session = None

        # Start session
        if not self.use_local:
            self.session = requests.Session()
            self.session.headers.update({
                "User-Agent": (
                    "WikiScraperStudentProject/1.0 "
                    "(educational use; jo469488@students.mimuw.edu.pl)"
                )
            })

        # Make sure the directory exists
        if self.cache_files and not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_soup(self, phrase: str) -> BeautifulSoup:
        """
        Fetches the content for a given phrase.

        Handles local file reading or network requests based on
        configuration.

        Args:
            phrase (str): The article title.

        Returns:
            soup (BeautifulSoup): The parsed HTML of the full page.
        """
        # Normalize the phrase
        safe_phrase = phrase.strip().replace(" ", "_")

        # Create a path for local use and caching
        file_path = os.path.join(self.data_dir, f"{safe_phrase}.html")

        # Get content from the local file
        if self.use_local:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    return BeautifulSoup(file, "html.parser")
            else:
                raise FileNotFoundError(f"File not found: '{file_path}'")

        # Prepare the url and get content from the site
        url = f"{self.base_url}/wiki/{safe_phrase}"
        response = self.session.get(url, timeout=5)
        response.raise_for_status()

        # Cache sites for local use
        if self.cache_files:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(response.text)
            except OSError:
                pass

        return BeautifulSoup(response.text, "html.parser")

    def _get_article_content(self, soup: BeautifulSoup):
        """
        Extracts the main content block from the page.

        Removes all the reference tags from the extracted text.

        Args:
            soup (BeautifulSoup): The parsed HTML of the full page.

        Returns:
            Tag: The HTML tag containing the main article content.
        """
        # Find the main article block
        content = soup.select_one("#mw-content-text .mw-parser-output")
        if not content:
            raise ValueError("Article content block not found")

        # Delete all reference notes
        for ref in content.select("sup.reference"):
            ref.decompose()

        return content

    def get_summary(self, phrase: str) -> str:
        """
        Retrieves the first non-empty paragraph of the article.

        Args:
            phrase (str): The article title.

        Returns:
            str: The summary text.
        """
        # Fetch site content
        soup = self._get_soup(phrase)

        # Get the main article from the site
        content = self._get_article_content(soup)

        # Get all the paragraphs and find the first one with text
        paragraphs = content.find_all("p", recursive=False)
        for p in paragraphs:
            text = p.get_text().strip()
            if text:
                return text

        raise ValueError("No summary paragraph found")

    def get_table(self, phrase: str, table_number: int) -> list[list[str]]:
        """
        Extracts data from a specific table in the article.

        Args:
            phrase (str): The article title.
            table_number (int): The 1-based index of the table to fetch.

        Returns:
            list[list[str]]: The table data as a list of rows.
        """
        # Fetch site content
        soup = self._get_soup(phrase)

        # Get the main article from the site
        content = self._get_article_content(soup)

        # Fetch all tables
        all_tables = content.find_all("table")

        # Filter out table containers
        tables = []
        for table in all_tables:
            if table.find("table"):
                continue
            tables.append(table)

        # Get the right table
        idx = table_number - 1
        if idx < 0 or idx >= len(tables):
            raise ValueError(
                f"Table #{table_number} not found. "
                f"Article has {len(tables)} tables."
            )
        target = tables[idx]

        # Extract data from the table
        try:
            dfs = pd.read_html(
                StringIO(str(target)),
                header=None,
                flavor='bs4'
            )
        except ValueError:
            return []

        if not dfs:
            return []

        # Normalize data and convert to text
        df = dfs[0]
        data = df.fillna("").astype(str).values.tolist()

        return data

    def count_words(self, phrase: str) -> dict[str, int]:
        """
        Counts occurrences of words in the article text.

        Removes punctuation, numbers, and single-letter words.

        Args:
            phrase (str): The article title.

        Returns:
            dict[str, int]: A dictionary mapping words to counts.
        """
        # Fetch site content
        soup = self._get_soup(phrase)

        # Get the main article from the site
        content = self._get_article_content(soup)

        # Get all the text
        text = content.get_text(separator=" ")

        # Seperate words, remove punctuation and normalize
        words = text.lower().split()
        clean_words = []
        translator = str.maketrans("", "", string.punctuation)
        for word in words:
            stripped_word = word.translate(translator)

            # Filter out single letter words and numbers
            if len(stripped_word) < 2:
                continue
            if stripped_word.isdigit():
                continue

            clean_words.append(stripped_word)

        # Count words
        return dict(Counter(clean_words))

    def get_valid_links(self, phrase: str) -> list[str]:
        """
        Finds valid internal Wiki links within the article.

        Filters out external links, special pages, and anchors.

        Args:
            phrase (str): The article title.

        Returns:
            list[str]: A list of clean Wiki phrases/titles found.
        """
        # Fetch site content
        soup = self._get_soup(phrase)

        # Get the main article from the site
        content = self._get_article_content(soup)

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

            phrase = unquote(href.split("/wiki/")[-1])
            if ":" not in phrase and "#" not in phrase:
                links.append(phrase)

        return links

    def close(self) -> None:
        """Closes the active HTTP session."""
        if self.session:
            self.session.close()
