import unittest

import pandas as pd

from web_of_marvel_characters.association import calculate_associations
from web_of_marvel_characters.utils import prepare_edges, process_appearances, visualization


class AnalysisTests(unittest.TestCase):
    def test_build_weights_df_returns_numeric_issue_columns(self) -> None:
        appearances = pd.DataFrame(
            {
                "character name": ["A", "B"],
                "Issue 1": ["Appearances", "Mentions"],
                "Issue 2": ["Minor Appearances", None],
            }
        )

        weights = prepare_edges.build_weights_df(appearances)

        self.assertEqual(weights.iloc[0, 1:].tolist(), [1.0, 0.5])
        self.assertEqual(weights.iloc[1, 1:].tolist(), [0.1, 0.0])
        self.assertTrue(all(dtype.kind == "f" for dtype in weights.iloc[:, 1:].dtypes))

    def test_filter_uses_matching_dataframe_labels(self) -> None:
        appearances = pd.DataFrame(
            {
                "character name": ["A", "B", "C"],
                "Issue 1": ["Appearances", "Appearances", None],
                "Issue 2": [None, "Appearances", "Appearances"],
            },
            index=[10, 20, 30],
        )
        stats = pd.DataFrame(
            {"Appearances": [1, 2, 1]},
            index=[10, 20, 30],
        )

        filtered = process_appearances.filter_less_frequent_characters(
            appearances,
            stats,
            top_n_characters=3,
            min_number_of_appearances=2,
        )

        self.assertListEqual(filtered.index.tolist(), [20])

    def test_linear_scale_handles_constant_values(self) -> None:
        self.assertEqual(visualization.linear_scale(4, 4, 4, 5, 50), 27.5)

    def test_association_measure_can_be_injected(self) -> None:
        weights = pd.DataFrame(
            {
                "character name": ["A", "B"],
                "Issue 1": [1.0, 0.0],
            }
        )
        expected = pd.DataFrame([[1.0, 0.5], [0.5, 1.0]], index=["A", "B"], columns=["A", "B"])

        def fake_measure(input_weights: pd.DataFrame) -> pd.DataFrame:
            self.assertIs(input_weights, weights)
            return expected

        result = calculate_associations(weights, fake_measure)

        pd.testing.assert_frame_equal(result, expected)


if __name__ == "__main__":
    unittest.main()
