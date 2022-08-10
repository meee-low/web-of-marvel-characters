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

def filter_less_frequent_characters(dataframe_to_modify:pd.DataFrame, key_df:pd.DataFrame,
                                    top_n_characters:int=None, min_number_of_apperances:int=None,
                                    character_percentile:float=None, min_frequency:float=None) -> pd.DataFrame:
    """
    Drop characters with different criteria:
        - Keep top n characters 
        - Keep top x% of characters
        - Keep characters with at least y appearances
        - Keep characters that show up in z% of issues in the selection
        
    Parameters
    ----------
    
    
    """
  
    number_of_characters_in_df = dataframe_to_modify.shape[0]
    # Both -> convert, compare and keep the most restrictive criterion
    # None-None -> keep all characters    
    # None-x% -> keep top x% of characters
    # n-None -> keep top n characters
    if top_n_characters != None and character_percentile != None:
        # select the most restrictive of the conditions:
        top_x_perc_characters = number_of_characters_in_df * character_percentile
        number_of_characters_to_keep = min(top_n_characters, top_x_perc_characters)
    elif top_n_characters != None:
        number_of_characters_to_keep = top_n_characters
    elif character_percentile != None:
        top_x_perc_characters = number_of_characters_in_df * character_percentile
        number_of_characters_to_keep = top_x_perc_characters
    else:
        number_of_characters_to_keep = number_of_characters_in_df
    # this relies on the 2 dataframes having the same index for the same characters.
    number_of_characters_to_keep = min(number_of_characters_to_keep, number_of_characters_in_df) # make sure we don't keep more than the number of characters in the dataframe
    number_of_characters_to_keep = int(number_of_characters_to_keep) # make sure we get an integer
    characters_to_keep_idx = key_df.sort_values(by="Appearances", ascending=False).head(number_of_characters_to_keep).index
    characters_to_keep = dataframe_to_modify.iloc[characters_to_keep_idx]
    
    # Now filter based on the number of appearances:
    number_of_issues_in_df = dataframe_to_modify.shape[1]
    if min_number_of_apperances != None and min_frequency != None:
        # select the most restrictive of the conditions:
        top_x_perc_appearances = number_of_issues_in_df * min_frequency
        min_appearances_to_keep = max(min_number_of_apperances, top_x_perc_appearances)
    elif min_number_of_apperances != None:
        min_appearances_to_keep = min_number_of_apperances
    elif min_frequency != None:
        top_x_perc_appearances = number_of_issues_in_df * min_frequency
        min_appearances_to_keep = top_x_perc_appearances
    else:
        min_appearances_to_keep = 0
    # this relies on the 2 dataframes having the same index for the same characters.
    min_appearances_to_keep = min(min_appearances_to_keep, number_of_issues_in_df) # make sure we don't filter out more than the max number of issues
    min_appearances_to_keep = int(min_appearances_to_keep) # make sure we get an integer
    characters_to_keep = characters_to_keep[key_df["Appearances"] >= min_appearances_to_keep]
     
    return characters_to_keep