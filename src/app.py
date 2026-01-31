"""
Application Controller Module.

This module acts as the central controller for the WikiScraper.
It initializes the Scraper, Analyzer, and Visualizer,
validates command-line arguments, and directs the flow of data between
these components based on the user's request.
"""

import time
import json
import os
import argparse
import requests

from .scraper import WikiScraper
from .analyzer import Analyzer
from .visualizer import Visualizer


class WikiApp:
    """
    Main application class governing the execution flow of the CLI tool.
    """

    def __init__(self, args: argparse.Namespace, base_url: str) -> None:
        """
        Initialize the application with parsed arguments and config.

        Args:
            args (argparse.Namespace): Parsed command-line arguments.
            base_url (str): The root URL for the Wiki to be scraped.
        """
        self.args = args
        self.word_counts_file = "word-counts.json"

        # Initialize modules
        self.scraper = WikiScraper(base_url)
        self.analyzer = Analyzer()
        self.visualizer = Visualizer()

    def _validate_arguments(self) -> None:
        """
        Validates dependencies between command-line arguments.

        Raises:
            ValueError: If required arguments are missing or invalid.
        """
        if self.args.table:
            if self.args.number is None:
                raise ValueError("Option --table requires argument --number!")
            if self.args.number < 1:
                raise ValueError(
                    "Argument --number must be >= 1.")

        elif self.args.auto_count_words:
            if self.args.depth is None or self.args.wait is None:
                raise ValueError(
                    "Option --auto-count-words requires "
                    "arguments --depth and --wait!"
                )
            if self.args.depth < 1:
                raise ValueError("Argument --depth must be >= 1.")
            if self.args.wait < 0:
                raise ValueError("Argument --wait cannot be negative.")

        elif self.args.analyze_relative_word_frequency:
            if self.args.mode is None or self.args.count is None:
                raise ValueError(
                    "Option --analyze-relative-word-frequency requires "
                    "arguments --mode and --count!"
                )
            if self.args.count < 1:
                raise ValueError("Argument --count must be >= 1.")
            if not os.path.exists(self.word_counts_file):
                raise ValueError(
                    f"Data file '{self.word_counts_file}' not found. "
                    "Run --count-words first."
                )

    def _handle_summary(self) -> None:
        """Fetches and prints the summary of the requested article."""
        summary = self.scraper.get_summary(self.args.summary)
        print(summary)

    def _handle_table(self) -> None:
        """Fetches a specific table, saves it, and shows statistics."""
        # Fetch the table raw data
        phrase = self.args.table
        raw_table = self.scraper.get_table(
            phrase,
            table_number=self.args.number
        )

        # Convert to pandas dataframe
        df = self.analyzer.create_dataframe(
            raw_table,
            first_row_is_header=self.args.first_row_is_header
        )

        # Save data to file
        filename = f"{phrase}.csv"
        df.to_csv(filename, header=self.args.first_row_is_header)

        # Show value frequencies stats
        stats_df = self.analyzer.get_value_frequencies(df)
        self.visualizer.print_pandas_table(stats_df)

    def _update_word_counts(self, phrase: str) -> None:
        """
        Counts words in a specific article.

        Gets results of word counts from a page and merges them
        into the JSON file.

        Args:
            phrase (str): The Wiki article title to scrape.
        """
        # Get word counts with current phrase
        new_counts = self.scraper.count_words(phrase)

        # Load overall word count from file
        global_data = {}
        if os.path.exists(self.word_counts_file):
            try:
                with open(self.word_counts_file, 'r', encoding='utf-8') as f:
                    global_data = json.load(f)
            except json.JSONDecodeError:
                print("[WARNING] JSON file corrupted, starting fresh.")

        # Merge new word counts in
        for word, count in new_counts.items():
            global_data[word] = global_data.get(word, 0) + count

        # Save new values to file
        with open(self.word_counts_file, 'w', encoding='utf-8') as f:
            json.dump(global_data, f, indent=4)

    def _handle_auto_crawl(self) -> None:
        """
        Performs a Breadth-First Search (BFS) crawl to count words.

        Starts from a given phrase and follows internal Wiki links
        up to a specified depth, updating the global word count file.
        """
        start_phrase = self.args.auto_count_words
        max_depth = self.args.depth
        wait_time = self.args.wait

        # Setup visitting queue and visited sites set
        queue = [(start_phrase, 0)]
        visited = set()

        # Crawl until there are links to visit
        while queue:
            current_phrase, depth = queue.pop(0)

            # Skip if visited, otherwise add to visited
            if current_phrase in visited:
                continue
            visited.add(current_phrase)

            # Print info about the current phrase
            print(f"[{depth}/{max_depth}] {current_phrase}")

            # Count words and update the file
            try:
                self._update_word_counts(current_phrase)
            except (requests.RequestException, OSError, ValueError) as e:
                print(f"[WARNING] Failed to process '{current_phrase}': {e}")

            # Find all the links if the set depth has not been reached yet
            if depth < max_depth:
                try:
                    links = self.scraper.get_valid_links(current_phrase)
                    for link in links:
                        if link not in visited:
                            queue.append((link, depth + 1))
                except requests.RequestException as e:
                    print(
                        f"[WARNING] Could not fetch links from "
                        f"'{current_phrase}': {e}"
                    )
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(
                        f"[WARNING] Failed to process "
                        f"'{current_phrase}': {e}"
                    )

            # Wait set amount of time
            if queue:
                time.sleep(wait_time)

    def _handle_analysis(self) -> None:
        """
        Performs statistical analysis on collected word counts.

        Generates a DataFrame comparing article word frequency
        vs language frequency and optionally plots the result.
        """
        # Check if we the data exists in a file
        if not os.path.exists(self.word_counts_file):
            raise ValueError(
                f"Error: {self.word_counts_file} not found. "
                "Run --count-words first."
            )

        # Load word count data from file
        with open(self.word_counts_file, 'r', encoding='utf-8') as f:
            article_counts = json.load(f)

        # Analyze all the data and create a dataframe
        df_results = self.analyzer.analyze_relative_frequency(
            article_counts,
            mode=self.args.mode,
            limit=self.args.count
        )

        # Print out the table
        self.visualizer.print_pandas_table(df_results)

        # Create and save the chart
        if self.args.chart:
            self.visualizer.plot_comparison(df_results, self.args.chart)

    def run(self) -> None:
        """Executes the main application logic with given arguments."""
        self._validate_arguments()
        if self.args.summary:
            self._handle_summary()
        elif self.args.table:
            self._handle_table()
        elif self.args.count_words:
            self._update_word_counts(self.args.count_words)
        elif self.args.auto_count_words:
            self._handle_auto_crawl()
        elif self.args.analyze_relative_word_frequency:
            self._handle_analysis()

    def close(self) -> None:
        """Closes external resources."""
        if self.scraper:
            self.scraper.close()
