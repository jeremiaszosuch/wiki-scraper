"""
Unit tests for the Visualizer module.

This module verifies that the `Visualizer` class correctly handles data
presentation. It mocks `matplotlib` functions to ensure that plotting
logic executes correctly without creating actual image files on the disk
during the test run.
"""

from unittest.mock import patch, MagicMock
import pytest
from pytest import CaptureFixture
import pandas as pd

from src.visualizer import Visualizer


@pytest.fixture(name="visualizer")
def fixture_visualizer() -> Visualizer:
    """Creates a Visualizer instance for tests."""
    return Visualizer()


class TestVisualizer:
    """Test suite for the Visualizer class."""

    def test_print_pandas_table(self, visualizer: Visualizer,
                                capsys: CaptureFixture[str]):
        """Tests if print_pandas_table outputs data to stdout."""
        df = pd.DataFrame({"A": [1, 2]})
        visualizer.print_pandas_table(df)

        # Capture stdout to verify the output
        captured = capsys.readouterr()
        assert "A" in captured.out
        assert "1" in captured.out

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_plot_comparison(self, mock_close: MagicMock,
                             mock_savefig: MagicMock, visualizer: Visualizer):
        """Tests if plot_comparison calls the savefig method."""
        df = pd.DataFrame({
            "word": ["a", "b"],
            "freq_article": [0.5, 0.2],
            "freq_lang": [0.1, 0.1]
        })

        visualizer.plot_comparison(df, "test.png")

        # Verify that matplotlib.pyplot.savefig was called with correct file
        mock_savefig.assert_called_with("test.png")
        mock_close.assert_called()
