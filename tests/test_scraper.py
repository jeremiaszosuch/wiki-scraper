"""
Unit tests for the WikiScraper class.
Tests HTML parsing and link filtering logic using mocks (no internet required).
"""

from unittest.mock import patch
from bs4 import BeautifulSoup
import pytest
from src.scraper import WikiScraper


@pytest.fixture(name="scraper")
def fixture_scraper():
    """Provide a fresh scraper for local use each test"""
    return WikiScraper(base_url="base_url", use_local=True)


@patch("src.scraper.WikiScraper._get_soup")
@patch("src.scraper.WikiScraper._get_article_content")
def test_valid_links_filtering(mock_content, mock_soup, scraper):
    """
    Checks link filtering.
    Should ignore external links (http) and system links (File:, Help:).
    """
    html_fragment = """
                    <div>
                        <p>
                            <a href="/wiki/Good_Link">Valid</a>
                            <a href="https://google.com">External</a>
                            <a href="/wiki/File:Image.jpg">File</a>
                            <a href="/wiki/Help:Contents">Special</a>
                        </p>
                    </div>
                    """
    soup_fragment = BeautifulSoup(html_fragment, "html.parser")

    # Configure mocks to return the created fragment
    mock_soup.return_value = soup_fragment
    mock_content.return_value = soup_fragment

    # Fetch the links
    links = scraper.get_valid_links("Any Phrase")

    # Assertions
    assert "Good_Link" in links
    assert "https://google.com" not in links
    assert "File:Image.jpg" not in links
    assert "Help:Contents" not in links


@patch("src.scraper.WikiScraper._get_soup")
@patch("src.scraper.WikiScraper._get_article_content")
def test_word_cleaning(mock_content, mock_soup, scraper):
    """
    Checks text cleaning:
    - Removes punctuation
    - Ignores numbers
    - Ignores words shorter than 2 characters
    """
    html_fragment = "<p>Hello, world! 123 a</p>"
    soup_fragment = BeautifulSoup(html_fragment, "html.parser")

    # Configure mocks to return the created fragment
    mock_soup.return_value = soup_fragment
    mock_content.return_value = soup_fragment

    # Execute counting words
    counts = scraper.count_words("Any Phrase")

    # Assertions
    assert counts.get("hello") == 1
    assert counts.get("world") == 1
    assert counts.get("123") is None
    assert counts.get("a") is None
