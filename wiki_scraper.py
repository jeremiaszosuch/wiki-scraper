import argparse
import sys
from src.scraper import WikiScraper

# Default base URL
DEFAULT_URL = "https://bulbapedia.bulbagarden.net"

def main():
    # Argument parser configuration
    parser = argparse.ArgumentParser(
        description=(
            "WikiScraper "
            "- A CLI tool for scraping and analyzing Wiki data."
        ),
        usage=(
            "\n"
            "  %(prog)s --summary PHRASE\n"
            "  %(prog)s --table PHRASE --number INT [--first-row-is-header]\n"
            "  %(prog)s --count-words PHRASE\n"
            "  %(prog)s --auto-count-words PHRASE --depth INT --wait FLOAT\n"
            "  %(prog)s --analyze-relative-word-frequency "
            "--mode {article,language} --count INT [--chart PATH]\n"
        )
    )

    # Main Actions
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument(
        "--summary", 
        type=str, 
        help=(
            "Fetches and displays the summary "
            "(first paragraph) of a given phrase."
        )
    )
    actions.add_argument(
        "--table", 
        type=str, 
        help="Fetches data from a specific table (requires --number)."
    )
    actions.add_argument(
        "--count-words", 
        type=str, 
        help="Counts words in the article and updates the JSON file."
    )
    actions.add_argument(
        "--auto-count-words", 
        type=str, 
        help=(
            "Recursively counts words starting from a phrase "
            "(requires --depth and --wait)."
        )
    )
    actions.add_argument(
        "--analyze-relative-word-frequency",
        action="store_true", 
        help=(
            "Analyzes relative word frequency "
            "(requires --mode and --count)."
        )
    )

    # Options and modifiers
    config = parser.add_argument_group("configuration")
    config.add_argument(
        "--number",
        type=int,
        help="The index of the table to fetch (1-based, for --table)."
    )
    config.add_argument(
        "--first-row-is-header",
        action="store_true",
        help="Force treating the first row as the header."
    )
    config.add_argument(
        "--depth",
        type=int,
        help="Recursion depth (for --auto-count-words)."
    )
    config.add_argument(
        "--wait",
        type=float,
        help="Wait time in seconds between requests."
    )
    config.add_argument(
        "--mode",
        type=str,
        choices=["article", "language"],
        help="Analysis mode (for --analyze...)."
    )
    config.add_argument(
        "--count",
        type=int,
        help="Number of top words to analyze."
    )
    config.add_argument(
        "--chart",
        type=str,
        help="Path to save the generated chart (optional)."
    )

    # Parse arguments
    args = parser.parse_args()

    # Initialize Scraper
    try:
        scraper = WikiScraper(base_url=DEFAULT_URL, use_local=False)
    except Exception as e:
        print(f"[ERROR] Failed to initialize scraper: {e}")
        sys.exit(1)
    
    # Action: Summary
    if args.summary:
        result = scraper.get_summary(args.summary)
        print(result)

    # Action: Table
    elif args.table:
        if not args.number:
            print("[ERROR] Option --table requires argument --number!")
            sys.exit(1)
        scraper.get_table(args.table, args.number, args.first_row_is_header)

    # Action: Count Words
    elif args.count_words:
        scraper.count_words(args.count_words) # TODO

    # Action: Auto Count Words
    elif args.auto_count_words:
        if not args.depth or not args.wait:
            print(
                "[ERROR] Option --auto-count-words "
                "requires arguments --depth and --wait!"
            )
            sys.exit(1)
        scraper.auto_count_words(args.auto_count_words, args.depth, args.wait) # TODO

    # Action: Analysis
    elif args.analyze_relative_word_frequency:
        if not args.mode or not args.count:
            print(
                "[ERROR] Option --analyze-relative-word-frequency "
                "requires arguments --mode and --count!"
            )
            sys.exit(1)
        # TODO analyzer.analyze(...)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
        sys.exit(0)