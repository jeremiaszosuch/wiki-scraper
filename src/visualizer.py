import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class Visualizer:
    def __init__(self) -> None:
        available_styles = plt.style.available
        if "bmh" in available_styles:
            plt.style.use("bmh")
        elif "ggplot" in available_styles:
            plt.style.use("ggplot")

    def print_pandas_table(self, df: pd.DataFrame) -> None:
        if df.empty:
            print("[WARNING] No available data to view.")
        else:
            with pd.option_context("display.max_rows", None,
                                   "display.max_columns", None,
                                   "display.width", 1000):
                print(df)

    def plot_comparison(self, df: pd.DataFrame, filename: str) -> None:
        if df.empty:
            print("[WARNING] No available data to plot.")
            return

        # Prepare data
        words = df["word"].tolist()
        freq_article = df["freq_article"].tolist()
        freq_lang = df["freq_lang"].tolist()

        # Set label positions and bar width
        x = np.arange(len(words))
        width = 0.35

        # Inititate the plot
        fig, ax = plt.subplots(figsize=(12, 6))

        # Create two bars next to each other
        ax.bar(x - width/2, freq_article, width,
               label="Article", color="skyblue")
        ax.bar(x + width/2, freq_lang, width,
               label="Language", color="orange")

        # Set scale
        ax.set_yscale("log")

        # Stylistic changes
        ax.set_ylabel("Frequency")
        ax.set_xticks(x)
        ax.set_xticklabels(words, rotation=45)
        ax.set_title("Word Frequency Comparison: Article vs Language")
        ax.grid(True, axis="y", which="major", linestyle="--", alpha=0.5)
        ax.legend()
        plt.tight_layout()

        # Save the plot to file
        try:
            plt.savefig(filename)
        except OSError as e:
            print(f"[ERROR] saving chart: {e}")
        finally:
            plt.close(fig)
