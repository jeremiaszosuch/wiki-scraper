"""
Unit tests for the WikiScraper module.

This module tests the HTML parsing capabilities of the `WikiScraper`
class. It utilizes mocking (unittest.mock) to simulate HTTP responses,
ensuring that tests run offline. The tests verify the extraction logic
for summaries, tables, internal links, and word counting.
"""

from unittest.mock import patch, MagicMock
import pytest

from src.scraper import WikiScraper


@pytest.fixture(name="sample_html")
def fixture_sample_html() -> str:
    """Provides an HTML string simulating a Wiki article structure."""
    return """
    <html>
        <body>
            <div id="mw-content-text">
                <div class="mw-parser-output">
                    <p>This is the <b>first</b> paragraph of the summary.</p>
                    <p>This is the second paragraph.</p>
                    
                    <table class="wikitable">
                        <tr><th>Col1</th><th>Col2</th></tr>
                        <tr><td>A</td><td>1</td></tr>
                        <tr><td>B</td><td>2</td></tr>
                    </table>

                    <ul>
                        <li><a href="/wiki/Internal_Link">Internal</a></li>
                        <li><a href="https://google.com">External</a></li>
                        <li><a href="/wiki/File:Image.jpg">File link</a></li>
                    </ul>
                </div>
            </div>
        </body>
    </html>
    """


@pytest.fixture(name="scraper")
def fixture_scraper() -> WikiScraper:
    """Creates a WikiScraper instance with a mock base URL."""
    return WikiScraper(base_url="base_url")


class TestWikiScraper:
    """
    Test suite for the WikiScraper class.

    Ensures correct HTML parsing and word counting logic without actual
    network requests.
    """

    @patch("requests.Session.get")
    def test_get_summary(self, mock_get: MagicMock,
                         scraper: WikiScraper, sample_html: str) -> None:
        """Tests if the summary is correctly extracted."""
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        summary = scraper.get_summary("test_article")

        # Check if HTML tags are stripped and text is correct
        assert summary == "This is the first paragraph of the summary."

    @patch("requests.Session.get")
    def test_get_table(self, mock_get: MagicMock,
                       scraper: WikiScraper, sample_html: str) -> None:
        """Tests if a table is correctly extracted into a list."""
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        table_data = scraper.get_table("test_article", 1)

        # Flatten the list of lists to check for existence of specific elements
        flat_data = [item for sublist in table_data for item in sublist]

        assert "A" in flat_data
        assert "1" in flat_data

    @patch("requests.Session.get")
    def test_count_words(self, mock_get: MagicMock,
                         scraper: WikiScraper) -> None:
        """Tests word counting logic, including normalizing data."""
        mock_response = MagicMock()

        # Simulating HTML content with punctuation and numbers
        mock_response.text = """
            <div id="mw-content-text"><div class="mw-parser-output">
            Hello world! Hello... world? 123
            </div></div>
        """
        mock_get.return_value = mock_response

        counts = scraper.count_words("test")

        # 'Hello' -> 'hello' (2 times), '123' should be ignored
        assert counts["hello"] == 2
        assert counts["world"] == 2
        assert "123" not in counts

    @patch("requests.Session.get")
    def test_get_valid_links(self, mock_get: MagicMock,
                             scraper: WikiScraper, sample_html: str) -> None:
        """Tests if the scraper correctly filters Wiki links."""
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        links = scraper.get_valid_links("test")

        # From sample_html:
        # /wiki/Internal_Link -> Valid
        # https://google.com  -> Invalid (External)
        # /wiki/File:Image.jpg -> Invalid (File)

        assert "Internal_Link" in links
        assert len(links) == 1
