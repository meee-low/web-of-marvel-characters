from collections.abc import Mapping

import pandas as pd

from ..association import calculate_associations

WEIGHTS_OF_APPEARANCES: dict[str, float] = {
    "Appearances": 1.0,
    "Minor Appearances": 0.5,
    "Mentions": 0.1,
    "Invocations": 0.0,
}


def build_weights_df(
    table: pd.DataFrame,
    weights_dict: Mapping[str, float] | None = None,
    fill_na: bool = True,
) -> pd.DataFrame:
    """Convert categorical appearances into a measure-ready wide table.

    The returned DataFrame has one row per character. Its first column is the
    original character-name column; every later column is one issue. Categorical
    values are replaced using ``weights_dict`` and converted to floats. Missing
    values become ``0.0`` when ``fill_na`` is true, which is the format expected
    by association measures.
    """
    if weights_dict is None:
        weights_dict = WEIGHTS_OF_APPEARANCES

    character_column = table.iloc[:, [0]].copy()
    appearance_values = table.iloc[:, 1:].replace(dict(weights_dict))
    appearance_values = appearance_values.apply(pd.to_numeric, errors="coerce")
    if fill_na:
        appearance_values = appearance_values.fillna(0.0)

    return pd.concat([character_column, appearance_values], axis=1)

def calculate_correlations(weights_df: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible alias for the default association measure."""
    return calculate_associations(weights_df)


def build_edge_list(corr_matrix:pd.DataFrame) -> pd.DataFrame:
    """
    Returns a dataframe with the source and target pairs as the first 2 columns, and an edge weight column as the third.
    """    
    # extract the edges from the correlation matrix
    # stack is like a pivot table. for each pair of (row, column), it finds the value of the corresponding cell.
    # This is a grouped dataframe. We reset the index to make it a regular dataframe.
    edges = corr_matrix.stack().reset_index()
    # label columns
    edges.columns = ["source", "target", "correlation"]
    # remove the edges from characters to themselves
    edges = edges[edges["source"] != edges["target"]]
    
    #note: not sure if I should reset the index here or not.
    
    return edges

def select_biggest_edges(edges:pd.DataFrame) -> pd.DataFrame:
    """
    Returns only the edges with the highest correlation for each source.
    
    Kept for compatibility with previous versions of the code. Use select_n_biggest_edges instead.
    """
    print("select_biggest_edges() is deprecated. Use select_n_biggest_edges() instead.")
    return select_n_biggest_edges(edges, 1)

def select_n_biggest_edges(edges:pd.DataFrame, n:int) -> pd.DataFrame:
    """
    Returns the top n edges with the highest correlation for each source.
    """
    edges_desc = edges.sort_values(by="correlation", ascending=False)
    grouped = edges_desc.groupby("source", sort=False, as_index=False)
    n_first = grouped.head(n)
    
    return n_first

def select_edges_above_threshhold(edges:pd.DataFrame, threshold:float) -> pd.DataFrame:
    """
    Returns only the edges with a correlation greater than the threshold.
    """
    edges_to_keep_bool = pd.Series(edges["correlation"] > threshold)
    edges = edges[edges_to_keep_bool]
    return edges

def filter_edges(edges:pd.DataFrame, soft_floor:float, hard_floor:float, top_n:int) -> pd.DataFrame:
    """
    Keep the edges that satisfy either of:
        - the correlation is above the soft floor
        - the correlation is above the hard floor and it's one of the n strongest edges for the source    
    
    Parameters
    ----------
    edges : pd.DataFrame
        the edges dataframe (columns: source, target, correlation)
    soft_floor : float
        All edges above this will be kept.
    hard_floor : float
        Any edge under this threshold will be removed, even if it's one of the top edges.
    top_n: int
        for each source, keep the top n edges
        
    Suggestion
    ----------
    soft_floor = 0.5
    hard_floor = 0.2
    top_n = 3
    """
    high_correlations  = select_edges_above_threshhold(edges, soft_floor)
    top_n_edges = select_n_biggest_edges(edges, top_n)
    #trim the top_n_edges to only include edges with a correlation greater than the hard threshold
    top_n_edges = top_n_edges[top_n_edges["correlation"] > hard_floor]
    
    return pd.concat([high_correlations, top_n_edges]).drop_duplicates()