import pandas as pd
import numpy as np
#from tqdm import tqdm

WEIGHTS_OF_APPEARANCES = {"Appearances":1,
                           "Minor Appearances":0.5,
                           "Mentions":0.1,
                           "Invocations":0}

def build_weights_df(table:pd.DataFrame, weights_dict:dict=WEIGHTS_OF_APPEARANCES, fill_na:bool=True) -> pd.DataFrame:
    """
    Converts the types of appearances to numeric values to be processed further (used in the correlation matrix).
    
    Uses the global variable WEIGHTS_OF_APPEARANCES to determine the weight of each appearance.
    """
    weights = table.copy() #copy table to variable weights to avoid changing the original table
    
    #turn the categories into numbers according to the global weights dictionary
    weights.iloc[:,1:] = weights.iloc[:,1:].astype('str').replace(weights_dict).astype(np.float64)
    
    #pd.to_numeric(weights.iloc[:,1:]) # turn into numbers
    if fill_na:
        weights = weights.fillna(0) # fill NaN (not an appearance in that issue) with 0
    #pd.to_numeric(weights.iloc[:,1:]) # turn into numbers again, to be sure
    weights.iloc[:,1:] = weights.iloc[:,1:].astype(np.float64)
    
    return weights

def calculate_correlations(weights_df:pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the correlation between each character.
    
    This takes in a weights_df where the columns are issues, the rows are characters and the values are numbers.
    """    
    #To use the .corr() method, we need the columns to be what we're correlating (i.e.: the characters).
    #Therefore, first we transpose the weights_df. Then we use the .corr() method to get the correlation matrix.
    weights_df_T = weights_df.T 
    
    # But this makes a lot of junk as a side effect:
    # The character names will become the first row, since that was the first column.
    # We want to make that first row the *header* and remove it from the data values.
    weights_df_T.columns = weights_df_T.iloc[0] # rename the column headers
    weights_df_T = weights_df_T.iloc[1:, :] # drop the first row
    
    weights_df_T = weights_df_T.astype(np.float64) # turn back into numbers, now that text is gone from the values
    
    corr_matrix = weights_df_T.corr() # get the correlation matrix properly
    corr_matrix.index.name = "" # cleanup: reset the index name (since it sets it to "character name" by default)
    return corr_matrix


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