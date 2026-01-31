"""
Unit tests for the main application logic (WikiApp).

This module tests the Command Line Interface (CLI) flow,
argument validation, and the orchestration between the scraper,
analyzer, and file system operations. It verifies that user inputs
trigger the correct methods in the underlying classes.
"""

# pylint: disable=protected-access

import argparse
from unittest.mock import patch, mock_open, MagicMock
import pytest
from pytest import CaptureFixture

from src.app import WikiApp


@pytest.fixture(name="mock_args")
def fixture_mock_args() -> argparse.Namespace:
    """Provides an argparse.Namespace object with default values."""
    return argparse.Namespace(
        summary=None, table=None, number=None, first_row_is_header=False,
        count_words=None, auto_count_words=None, depth=None, wait=None,
        analyze_relative_word_frequency=False, mode=None, count=None,
        chart=None
    )


class TestWikiApp:
    """Test suite for the WikiApp class."""

    def test_validate_arguments_error(
        self,
        mock_args: argparse.Namespace
    ) -> None:
        """
        Test missing argument handling.

        Check if the application raises a ValueError when a required
        dependency argument is missing.
        """
        mock_args.table = "test_page"
        mock_args.number = None

        app = WikiApp(mock_args, "base_url")

        with pytest.raises(ValueError, match="requires argument --number"):
            app._validate_arguments()

    @patch("src.app.WikiScraper")
    def test_handle_summary_execution(
        self,
        mock_scraper: MagicMock,
        mock_args: argparse.Namespace,
        capsys: CaptureFixture[str]
    ) -> None:
        """
        Tests the execution flow for the --summary command.

        Ensures the scraper is called and the result is printed.
        """
        # Setup
        mock_args.summary = "test_page"
        mock_instance = mock_scraper.return_value
        mock_instance.get_summary.return_value = "This is a summary."

        app = WikiApp(mock_args, "base_url")
        app.run()

        # Verification
        captured = capsys.readouterr()
        assert "This is a summary." in captured.out

    @patch("src.app.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"hello": 5}')
    @patch("src.app.json.dump")
    @patch("src.app.WikiScraper")
    def test_update_word_counts(
        self,
        mock_scraper: MagicMock,
        mock_json_dump: MagicMock,
        mock_file: MagicMock,
        mock_exists: MagicMock,
        mock_args: argparse.Namespace
    ) -> None:
        """
        Tests the logic for updating the word-counts.json file.

        Verifies if new counts are correctly merged with existing data.
        """
        # Mocking the scraper to return new counts
        mock_instance = mock_scraper.return_value
        mock_instance.count_words.return_value = {"hello": 2, "world": 1}

        # Mock file existance
        mock_exists.return_value = True

        app = WikiApp(mock_args, "base_url")
        app._update_word_counts("test_page")

        # Verify the merged data that was passed to json.dump
        # Existing 'hello': 5, New 'hello': 2 -> Total: 7
        args, _ = mock_json_dump.call_args
        data_saved = args[0]

        mock_file.assert_called_with("word-counts.json", "w", encoding="utf-8")
        assert data_saved["hello"] == 7
        assert data_saved["world"] == 1
