"""
Visualization and Output Module.

This module handles the presentation of data to the user. It includes
utilities for printing full Pandas DataFrames to the console and
generating matplotlib charts for frequency analysis.
"""

import matplotlib.pyplot as plt
import pandas as pd


class Visualizer:
    """
    A helper class for printing tables and plotting charts.
    """

    def __init__(self) -> None:
        """
        Initialize the visualizer and set the matplotlib style.
        """
        available_styles = plt.style.available
        if "bmh" in available_styles:
            plt.style.use("bmh")
        elif "ggplot" in available_styles:
            plt.style.use("ggplot")

    def print_pandas_table(self, df: pd.DataFrame) -> None:
        """
        Prints a Pandas DataFrame to stdout without truncation.

        Args:
            df (pd.DataFrame): The DataFrame to print.
        """
        if df.empty:
            print("[WARNING] No available data to view.")
        else:
            with pd.option_context("display.max_rows", None,
                                   "display.max_columns", None,
                                   "display.width", 1000):
                print(df)

    def plot_comparison(self, df: pd.DataFrame, filename: str) -> None:
        """Creates a bar chart comparing word frequency.

        Generates and saves a bar chart comparing
        article vs. language word frequency.

        Args:
            df (pd.DataFrame): Data containing 'freq_article'
                and 'freq_lang'.
            filename (str): The path where the chart image
                will be saved.
        """
        if df.empty:
            print("[WARNING] No available data to plot.")
            return

        # Set up data
        plot_data = df.set_index("word")[["freq_article", "freq_lang"]]
        plot_data = plot_data.fillna(0)

        # Add column labels
        plot_data.columns = ["Article", "Language"]

        # Initialize plot
        fig, ax = plt.subplots(figsize=(12, 6))

        # Draw the plot
        plot_data.plot(
            kind="bar",
            ax=ax,
            width=0.7,
            logy=True,
            color=["skyblue", "orange"]
        )

        # Stylistic changes
        ax.set_ylabel("Frequency")
        ax.set_xlabel("")
        ax.set_title("Word Frequency Comparison: Article vs Language")
        ax.grid(True, axis="y", which="major", linestyle="--", alpha=0.5)
        plt.tight_layout()

        # Save the plot to file
        try:
            plt.savefig(filename)
        except OSError as e:
            print(f"[ERROR] saving chart: {e}")
        finally:
            plt.close(fig)
