from unicodedata import category
import pandas as pd
from utils import scrape, aliases
from bs4 import BeautifulSoup
from tqdm import tqdm
from pandas.api.types import CategoricalDtype
import numpy as np

"""
The goal of this module is to take in a list of issues and return a dataframe.
Input: list of issues. Each element is a dictionary with the "title" and "url" of the issue.
Output: dataframe of appearances.
    Dataframe format:
    - rows: character names
    - columns: issue title and number
    - values: type of appearance
"""

TYPE_OF_APPEARANCE = CategoricalDtype(categories=["Mentions", "Minor Appearances", "Appearances"], ordered=True)

def build_full_table(issues:list, save_progress=True) -> pd.DataFrame:
    """ Takes in a list of issues and urls, and returns a table of appearances. """
    def save_full_table(main_table:pd.DataFrame, path:str="data/table_of_appearances.csv") -> None:
        """Save the full table to a csv."""
        if save_progress:
            main_table.to_csv(path, index=False)

    main_table = pd.DataFrame({'character name': pd.Series(dtype='str')}) #initialize first column
    for i, issue in enumerate(tqdm(issues)):
        # iterate through each issue in the list of issues.
        issue_table = build_issue_table(issue) # make a column with the values of the issue
        main_table = append_issue_column_to_main_table(main_table, issue_table) # merge to the main table as you go
        if i % 10 == 0:
            # every 10 issues, save it to the file
            save_full_table(main_table)
    save_full_table(no_dupes)
    
    # remove duplicates:
    no_dupes = remove_duplicates(main_table)
    
    # swap the names for the hero names:
    # this has to be done at the end because we use the default names as unique identifiers when merging the issues
    replace_aliases(no_dupes)
    
    #finally, save and return it
    save_full_table(no_dupes)
    return no_dupes

def build_issue_table(issue:dict) -> pd.DataFrame:
    """
    Runs a battery of functions.
    Returns a table with the type of appearance for every character in the issue.
    """
    def list_characters_in_issue(soup:BeautifulSoup) -> pd.DataFrame:
        """Takes in the url of an issue and returns a pandas dataframe of characters in the issue."""
        categories = soup.find_all("ul", class_="categories")[0].find_all("span", class_="name")
        
        issue_table = []
        for c in categories:
            a_tag = c.find("a")
            u, name = a_tag.get("href"), a_tag.get("title")
            if "(Earth-" in name:
                # Problem: "Categories" typically include items, locations etc. that are not characters.
                # Characters always include the universe they are from. (e.g. 'Earth-616').
                # Since we want only characters, we need to filter out the ones that are not characters.
                
                #characters_in_issue.append({"url": u, "name": name}) # not used anymore
                issue_table.append({"character name": name})
        issue_table = pd.DataFrame(issue_table)
        
        return issue_table
    
    def clean_characters_names(issue_table : pd.DataFrame) -> pd.DataFrame:
        """
        Remove the prefix "Category:" from the name.
        Additionally, if the character is from Earth-616, the default universe, that doesn't need to be specified,
        so we remove it from the name.
        """
        issue_table["character name"] = issue_table["character name"].str.replace("Category:", "")
        issue_table["character name"] = issue_table["character name"].str.replace(" \(Earth-616\)", "", regex=True)
        #reminder: parenthesis are special characters in regex. They need to be escaped.
        
        return issue_table

    def split_type_of_appearance(issue_table : pd.DataFrame, issue_name:str) -> pd.DataFrame:
        """
        Makes a new column with the type of appearance, then removes it from the name.
        The title of the column is the title + number of the issue.
        """
        # The expected input will be something like "Scott Summers/Appearance"
        # We split it at the '/'. The first half is the name, the second half is the kind of appearance.
        # The kind of appearance is then moved to the new column.
        
        # The last bit is the kind of appearance.
        issue_table[issue_name] = issue_table["character name"].str.split("/").str[-1]
        #change the type of the series/column to category.
        issue_table[issue_name] = issue_table[issue_name].astype(TYPE_OF_APPEARANCE)
        
        # All the earlier bits (usually 1), will be the name.
        # We use str.join to join the bits back together to be safe just in case there's a '/' in the name itself.
        issue_table["character name"] = issue_table["character name"].str.split("/").str[:-1].str.join("/")
        
        # Only keep the rows that are "Appearances", "Minor Appearances" or "Mentions".
        # No longer necessary with category type.
        # issue_table = issue_table[issue_table[issue_name].isin(["Appearances", "Minor Appearances", "Mentions"])]
        
        return issue_table
    
    #unpack the issue dictionary
    issue_name, issue_url = issue["title"], issue["url"]
    issue_soup = scrape.soup_from_url(issue_url)
    
    issue_table = list_characters_in_issue(issue_soup)
    issue_table = clean_characters_names(issue_table)
    issue_table = split_type_of_appearance(issue_table, issue_name)
    return issue_table

def append_issue_column_to_main_table(main_table:pd.DataFrame, issue_table:pd.DataFrame) -> pd.DataFrame:
    """Appends the new issue column to the main table."""
    main_table = main_table.merge(issue_table, on="character name", how="outer")
    return main_table

def remove_duplicates(main_table:pd.DataFrame) -> pd.DataFrame:
    """
    Removes duplicate rows.
    """
    main_table_no_dupes = main_table.groupby("character name", as_index=False, sort=False).max()
    
    return main_table_no_dupes

def replace_aliases(main_table:pd.DataFrame) -> pd.DataFrame:
    """
    Replaces the character names for their aliases, as specified in the aliases module.
    """
    main_table["character name"].replace(aliases.ALIASES, regex=False, inplace=True)
    return main_table

def main():
    build_full_table(scrape.build_full_list_of_issues())

if __name__ == "__main__":
    main()