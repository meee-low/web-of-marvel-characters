import pandas as pd

def count_types_of_appearances(table:pd.DataFrame, sort=True) -> pd.DataFrame:
    """For each character in the table, count the number of each type of appearance."""
    characters = pd.DataFrame({"character name":    pd.Series(table["character name"]), 
                               "Appearances":       pd.Series((table.iloc[:,1:] == "Appearances").sum(axis=1)),
                               "Minor Appearances": pd.Series((table.iloc[:,1:] == "Minor Appearances").sum(axis=1)),
                               "Mentions":          pd.Series((table.iloc[:,1:] == "Mentions").sum(axis=1))})
    
    characters["Total Appearances (Full and Minor)"] = characters["Appearances"] + characters["Minor Appearances"]
    characters["Appearances and Mentions (Full + Minor + Mentions)"] = characters["Total Appearances (Full and Minor)"] + characters["Mentions"]
    
    if sort:
        characters.sort_values(by="Appearances", ascending=False, inplace=True)
    
    return characters

def drop_less_relevant_characters(dataframe_to_modify:pd.DataFrame, key_df:pd.DataFrame, column:str, threshold:int) -> pd.DataFrame:
    """Drop characters with less than a certain number of appearances."""
    result = dataframe_to_modify[key_df[column] >= threshold]
    result.reset_index(drop=True, inplace=True)
    return result