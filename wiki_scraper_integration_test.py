import os
from src.scraper import WikiScraper

TEST_PHRASE = "Team_Rocket"
EXPECTED_START = "Team Rocket"
EXPECTED_END = "outpost in the Sevii Islands."


def main():
    # Check if the local file exists
    file_path = os.path.join("data", f"{TEST_PHRASE}.html")
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Local file missing: {file_path}. "
            "You need to create it in 'data' folder."
        )

    scraper = None
    try:
        # Initialize scraper
        scraper = WikiScraper(base_url="base_url", use_local=True)

        # Execute action
        summary = scraper.get_summary(TEST_PHRASE)

        # Test if the output is correct
        assert summary.startswith(EXPECTED_START), (
            f"\nTEXT MISMATCH!\n"
            f"Expected to start with: '{EXPECTED_START}'\n"
            f"Got: '{summary[:len(EXPECTED_START)]}'"
        )
        assert summary.endswith(EXPECTED_END), (
            f"\nTEXT MISMATCH!\n"
            f"Expected to end with: '{EXPECTED_END}'\n"
            f"Got: '{summary[-len(EXPECTED_END):]}'"
        )

    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
