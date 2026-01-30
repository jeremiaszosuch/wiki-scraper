"""
Unit tests for the Analyzer class.
Tests data processing, dataframe creation, and frequency analysis logic.
"""

import pytest
from src.analyzer import Analyzer


@pytest.fixture(name="analyzer")
def fixture_analyzer():
    """Provide a fresh Analyzer each test"""
    return Analyzer(language_code='en')


def test_create_dataframe_logic(analyzer):
    """
    Check if create_dataframe correctly sets the first column as
    the INDEX.
    """
    raw_data = [
        ["Pokemon", "Type 1", "Type 2"],
        ["Bulbasaur", "Grass", "Poison"],
        ["Charmander", "Fire", ""]
    ]

    df = analyzer.create_dataframe(raw_data, first_row_is_header=True)

    # Check if index is correct
    assert df.index.name == "Pokemon"
    assert "Bulbasaur" in df.index

    # Check if column is correct
    assert "Type 1" in df.columns

    # Ensure the index column is not duplicated in the main columns
    assert "Pokemon" not in df.columns


def test_normalization(analyzer):
    """
    Ensure analyze_relative_frequency correctly counts and normalizes
    the values.
    """
    # Mock input data
    article_counts = {"pikachu": 50}

    df = analyzer.analyze_relative_frequency(
        article_counts, mode="article", limit=5
    )

    # Get the result row for 'pikachu' using a boolean mask
    row = df[df['word'] == 'pikachu'].iloc[0]

    # Check if freq_article is 1.0
    assert row['freq_article'] == pytest.approx(1.0)

    # Check if the column structure is correct
    expected_cols = ['word', 'freq_article', 'freq_lang']
    assert list(df.columns) == expected_cols
