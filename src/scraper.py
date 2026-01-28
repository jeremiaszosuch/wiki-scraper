from bs4 import BeautifulSoup
import requests
import os

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
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
        
    def get_summary(self, phrase: str) -> str:
        # Fetch site content
        soup = self._get_soup(phrase)
        
        # Find the right article block
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