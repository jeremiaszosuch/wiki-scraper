from bs4 import BeautifulSoup
import requests
import os

class WikiScraper:
    def __init__(self, base_url, use_local=False, cache_dir="data"):
        self.base_url = base_url
        self.use_local = use_local
        self.cache_dir = cache_dir
        
        # Make sure the folder exists
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
    def _get_headers(self):
        return {
            "User-Agent": (
                "WikiScraperStudentProject/1.0 "
                "(educational use; jo469488@students.mimuw.edu.pl)"
            )
        }

    def _get_soup(self, phrase):
        # Normalize the phrase
        safe_phrase = phrase.strip().replace(" ", "_")
        
        # Prepare the file path
        filename = f"{safe_phrase}.html"
        file_path = os.path.join(self.cache_dir, filename)
        
        # Get content from the local file
        if self.use_local:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    return BeautifulSoup(file, "html.parser")
            else:
                raise FileNotFoundError(f"File not found: '{file_path}'")
            
        # Prepare the url and get content from the site
        url = f"{self.base_url}/wiki/{safe_phrase}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        # Cache the response for future use or debugging
        if self.cache_dir:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
        
        return BeautifulSoup(response.text, "html.parser")
        
    def get_summary(self, phrase):
        # Try to fetch site content
        try:
            soup = self._get_soup(phrase)
        except FileNotFoundError as e:
            return f"[FileError] {e}"
        except requests.exceptions.RequestException as e:
            return f"[NetworkError] {e}"
        except Exception as e:
            return f"[Error] {e}"
        
        # Find the right article block
        content = soup.select_one("#mw-content-text .mw-parser-output")
        if not content:
            return "[Error] Article content not found"
        
        # Get all the paragraphs and find the first one with text
        paragraphs = content.find_all("p", recursive=False)
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                return text
        return "[Error] No text paragraph found"