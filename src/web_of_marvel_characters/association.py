from collections.abc import Callable

import numpy as np
import pandas as pd


AssociationMeasure = Callable[[pd.DataFrame], pd.DataFrame]


def pearson_association(weights_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the current Pearson association matrix.

    Parameters
    ----------
    weights_df:
        A wide DataFrame produced by ``build_weights_df``. Each row is one
        character. The first column contains character names and is excluded
        from the calculation. Every remaining column represents one issue and
        contains numeric appearance weights, normally ``0.0``, ``0.1``,
        ``0.5``, or ``1.0``.

    Returns
    -------
    pandas.DataFrame
        A square character-by-character matrix. Its index and columns contain
        the character names in the same order as ``weights_df``. Each cell is
        the association score for that pair; the diagonal represents a
        character paired with itself.

    Notes
    -----
    A future association measure should accept exactly this input shape and
    return the same output shape. It should not include the character-name
    column in its calculation.
    """
    values = weights_df.set_index(weights_df.columns[0]).T.astype(np.float64)
    associations = values.corr()
    associations.index.name = None
    associations.columns.name = None
    return associations


def calculate_associations(
    weights_df: pd.DataFrame,
    measure: AssociationMeasure = pearson_association,
) -> pd.DataFrame:
    """Run a pluggable association measure over weighted appearances.

    ``weights_df`` must be a wide DataFrame with one row per character, a
    character-name column first, and one numeric column per issue. The first
    column is metadata and must not be scored as an issue. Missing appearance
    values should already have been converted to numeric zeros by
    ``build_weights_df``.

    ``measure`` receives that DataFrame and must return a square DataFrame
    whose index and columns contain the same character labels in the same
    order. The returned values are the pairwise association scores consumed
    by ``build_edge_list``. This function validates the matrix shape and label
    alignment, but does not validate the meaning or scale of the scores.
    """
    associations = measure(weights_df)
    if associations.shape[0] != associations.shape[1]:
        raise ValueError("An association measure must return a square matrix")
    if not associations.index.equals(associations.columns):
        raise ValueError("Association matrix index and columns must match")
    return associations