"""
Unit tests for the Visualizer module.

This module verifies that the `Visualizer` class correctly handles
data presentation. It mocks `matplotlib` functions to ensure that
plotting logic executes correctly without creating actual image files
on the disk during the test run.
"""

from unittest.mock import patch, MagicMock
import pandas as pd
import pytest

from src.analyzer import Analyzer


@pytest.fixture(name="analyzer")
def fixture_analyzer() -> Analyzer:
    """Creates a fresh instance of the Analyzer class for each test."""
    return Analyzer()


class TestAnalyzer:
    """
    Test suite for the Analyzer class.

    Checks Analyzer class data manipulation and frequency analysis.
    """

    def test_create_dataframe_with_headers(self, analyzer: Analyzer) -> None:
        """Tests creating a DataFrame with the header."""
        raw_data = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]

        df = analyzer.create_dataframe(raw_data, True)

        assert not df.empty
        assert list(df.columns) == ["Age"]
        assert df.index.name == "Name"
        assert "Alice" in df.index

    def test_create_dataframe_no_headers(self, analyzer: Analyzer) -> None:
        """Tests creating a DataFrame without headers."""
        raw_data = [["Alice", "30"], ["Bob", "25"]]
        df = analyzer.create_dataframe(raw_data, False)

        assert len(df) == 2
        assert df.shape[1] == 1

    def test_get_value_frequencies(self, analyzer: Analyzer) -> None:
        """Tests the calculation of value frequencies."""
        df = pd.DataFrame({
            "Col1": ["A", "B", "A"],
            "Col2": ["C", "C", "D"]
        })
        stats = analyzer.get_value_frequencies(df)

        # Expected: A=2, B=1, C=2, D=1. Total 6 items.
        assert "Value" in stats.columns
        assert "Count" in stats.columns

        row_a = stats[stats["Value"] == "A"]
        assert row_a["Count"].values[0] == 2

    @patch("src.analyzer.word_frequency")
    @patch("src.analyzer.top_n_list")
    def test_analyze_relative_frequency(
        self,
        mock_top_n: MagicMock,
        mock_word_freq: MagicMock,
        analyzer: Analyzer
    ) -> None:
        """
        Tests the relative frequency analysis logic.

        Mocks:
            wordfreq.top_n_list: To return a list of top words.
            wordfreq.word_frequency: To return frequency values.
        """
        # Mocking the external library behavior
        mock_top_n.return_value = ["the", "is", "a"]
        mock_word_freq.side_effect = lambda w, l: 0.1 if w == "the" else 0.01

        article_counts = {"the": 10, "unique": 5}

        df = analyzer.analyze_relative_frequency(
            article_counts, mode="language", limit=3)

        assert len(df) == 3
        assert "freq_article" in df.columns
        assert "freq_lang" in df.columns
