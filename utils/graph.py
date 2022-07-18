import pandas as pd
import numpy as np
from tqdm import tqdm

WEIGHTS_OF_APPEARANCES = {"Appearances":10,
                           "Minor Appearances":2,
                           "Mentions":0,
                           "Invocations":0}

#IDEA:
# USE NUMPY matrix multiplication to calculate the weight of the connection.
# Convert the strings of types of appearances to numbers.
# Then you get a new dataframe which is composed of:
# first column: source, second column: target
# all other columns: issues, with the values being the result of a matrix operation between the two characters.
# in the end, just add up the issue columns to get the weight of the connection.

def build_weights_df(table:pd.DataFrame) -> pd.DataFrame:
    # change the type of appearance to a number based on the weights
    weights = table.iloc[:,1:].copy() #copy table to variable weights to avoid changing the original table
    weights = weights.replace(WEIGHTS_OF_APPEARANCES).fillna(0).astype(int) #turn into numbers
    # multiply matrix weights and the transpose of weights
    weights_multiplied = np.matmul(np.asarray(weights), np.transpose(weights))
    result = pd.concat((table["character name"], weights_multiplied), axis=1)
    
    return result

def build_edge_list(weights_df:pd.DataFrame) -> list:
    # create a list of edges from the weights_df
    edges = []
    with tqdm(total=len(weights_df)) as pbar:
        for i, char1 in weights_df["character name"].iloc[:-1].iteritems():
            for j, char2 in weights_df["character name"].iloc[i+1:].iteritems():
                # iterate through the top-right triangle of the matrix
                weight = weights_df.iloc[i,j+1]
                edges.append({"source":char1, "target":char2, "weight":weight})
            pbar.update(1)
    edges = pd.DataFrame(edges)
    
    return edges