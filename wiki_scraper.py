import argparse
import sys
from src.app import WikiApp

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

    # Main actions
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

    # Actions modifiers
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

    # Initialize the app
    app = WikiApp(args, DEFAULT_URL)
    try:
        app.run()
    except KeyboardInterrupt:
        print("[INFO] Operation interrupted by user. Exiting...")
        sys.exit(0)
    except ValueError as e:
        print(f"[ERROR] Validation failed: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"[ERROR] System error: {e}")
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        app.close()


if __name__ == "__main__":
    main()
