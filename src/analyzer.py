"""
Logic for data processing and statistical analysis.

This module handles the conversion of raw data into Pandas DataFrames,
performs frequency analysis using the 'wordfreq' library, and prepares
data for visualization.
"""

import pandas as pd
from wordfreq import word_frequency, top_n_list


class Analyzer:
    """A helper class for analyzing and structuring table data"""

    def __init__(self, language_code: str = "en"):
        """
        Initialize the analyzer with a specific language.

        Args:
            language_code (str): ISO 639-1 language code (def: 'en').
        """
        self.lang = language_code

    def create_dataframe(self, raw_data: list[list[str]],
                         first_row_is_header: bool) -> pd.DataFrame:
        """
        Converts raw list-of-lists data into a Pandas DataFrame.

        Automatically sets the first column as the index if possible.

        Args:
            raw_data (list[list[str]]): The raw table data.
            first_row_is_header (bool): Whether to treat the first row
                                        as column headers.

        Returns:
            pd.DataFrame: The processed DataFrame (empty on failure).
        """
        if not raw_data:
            return pd.DataFrame()

        try:
            # Check if there are columnd headers
            if first_row_is_header and len(raw_data) > 1:
                headers = raw_data[0]
                data = raw_data[1:]
                df = pd.DataFrame(data, columns=headers)
            else:
                df = pd.DataFrame(raw_data)

            # Set first column as index
            if not df.empty and df.shape[1] > 0:
                df.set_index(df.columns[0], inplace=True)

            return df
        except ValueError as e:
            print(f"[ERROR] Failed to convert table to DataFrame: {e}")
            return pd.DataFrame()

    def get_value_frequencies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the frequency of every unique value.

        Args:
            df (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: A DataFrame with columns ['Value', 'Count'].
        """
        if df.empty:
            return pd.DataFrame()

        stats = df.stack().value_counts().reset_index()
        stats.columns = ["Value", "Count"]
        return stats

    def analyze_relative_frequency(self, article_counts: dict[str, int],
                                   mode: str, limit: int) -> pd.DataFrame:
        """
        Compares word usage in articles against general language usage.

        Calculates relative frequencies and normalizes them.

        Args:
            article_counts (dict): Dictionary mapping words to counts.
            mode (str): 'article' (top words from article) or
                'language' (top common words from language).
            limit (int): The number of top words to analyze.

        Returns:
            pd.DataFrame: A DataFrame containing normalized frequencies
                for the article and the language.
        """
        # Check if there is any article word data
        if not article_counts:
            return pd.DataFrame()
        total_article_words = sum(article_counts.values())
        if total_article_words == 0:
            return pd.DataFrame()

        # Sort data based on language
        if mode and "language" in mode.lower():
            # Get top n words from language
            top_words = top_n_list(self.lang, limit)
            df = pd.DataFrame(top_words, columns=["word"])

            # Get frequency for each word
            df["freq_lang"] = df["word"].apply(
                lambda w: word_frequency(w, self.lang)
            )

            # Map article word count data
            df["count"] = df["word"].map(article_counts).fillna(0)

            # Calculate article words frequencies
            df["freq_article"] = df["count"] / total_article_words

        # Sort data based on article
        else:
            # Create a dataframe from word count data
            df = pd.DataFrame(list(article_counts.items()),
                              columns=["word", "count"])

            # Calculate article words frequencies
            df["freq_article"] = df["count"] / total_article_words

            # Sort data in descending order
            df = df.sort_values(by="count", ascending=False).head(limit)

            # Add language words frequencies
            df["freq_lang"] = df["word"].apply(
                lambda w: word_frequency(w, self.lang)
            )

        # Normalize article frequency
        max_art = df["freq_article"].max()
        if max_art > 0:
            df["freq_article"] = df["freq_article"] / max_art

        # Normalize language frequency
        max_lang = df["freq_lang"].max()
        if max_lang > 0:
            df["freq_lang"] = df["freq_lang"] / max_lang

        return df[["word", "freq_article", "freq_lang"]]
