import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import math
from tqdm import tqdm
from tqdm.contrib import tzip
import networkx as nx


#set up logging
logging.basicConfig(filename = "error.log", encoding='utf-8', level=logging.INFO)


WEIGHTS_OF_APPEARANCES = {"Appearances":10,
                           "Minor Appearances":2,
                           "Mentions":0,
                           "Invocations":0}

TITLES_TO_DOWNLOAD = [{"title": "X-Men Vol 1",         "first_issue": 94,  "last_issue": 141},
                      {"title": "Uncanny X-Men Vol 1", "first_issue": 142, "last_issue": 280},
                      {"title": "New Mutants Vol 1",   "first_issue": 1,   "last_issue": 100},
                      {"title": "X-Factor Vol 1",      "first_issue": 1,   "last_issue": 70},
                      {"title": "Excalibur Vol 1",     "first_issue": 1,   "last_issue": 41},
                      {"title": "X-Force Vol 1",       "first_issue": 1,   "last_issue": 15}]

def soup_from_url(url:str, retries=0, max_retries=3):
    """
    Returns the soup from the url. If it fails, tries a maximum of max_retries times.
    """
    response = requests.get(url)    
    soup = BeautifulSoup(response.content, "html.parser")
    
    if response.status_code == 200:
        # All good. Return.
        return soup
    elif retries <= max_retries: #retry at most this many tries
        error_message = f"Tried to scrape and failed.   " \
                        f"Response code: {response.status_code}   " \
                        f"Tries: {retries}   " \
                        f"len(soup): {len(soup)}   " \
                        f"len(response.content()): {len(response.content)}   " \
                        f"URL: {url.split('/')[-1]}"
        logging.warning(error_message)
        return url_to_soup(url, retries=retries+1)
    else:
        logging.error(f"Tried too many times and failed. Exiting.")
        assert False #assert False is bad practice. create an err.
        
        
def create_list_of_issues(prefix:str, title:str, first_issue:int, last_issue:int):
    """
    Return a list of issues of the format prefix + title + issue_number.
    """
    issues = []
    for i in range(first_issue, last_issue+1):
        issues.append(prefix + title + " " + str(i))
    return issues
    
def create_list_of_issue_urls_from_marvel_wiki(title:str, first_issue:int, last_issue:int):
    """
    Return a list of issue urls of the format prefix + title + issue_number.
    """
    prefix = "https://marvel.fandom.com/wiki/"
    unformatted_urls = create_list_of_issues(prefix, title, first_issue, last_issue)
    urls = []
    for url in unformatted_urls:
        url = space_to_underscores(url)
        url = remove_special_characters(url)
        urls.append(url)
    return urls

def create_list_of_titles(title:str, first_issue:int, last_issue:int):
    prefix = ""
    return create_list_of_issues(prefix, title, first_issue, last_issue)
        

def space_to_underscores(string):
    """
    Replace spaces with underscores.
    """
    return string.replace(" ", "_")

def remove_special_characters(string):
    """
    Remove special characters from a string.
    """
    allowed_characters = "_/:.-?"
    return "".join(e for e in string if e.isalnum() or e in allowed_characters)


def list_characters_in_issue(url:str) -> pd.DataFrame:
    """
    Takes in the url of an issue and returns a pandas dataframe of characters in the issue.
    """
    soup = soup_from_url(url)
    categories = soup.find_all("ul", class_="categories")[0].find_all("span", class_="name")
    
    characters_in_issue = []
    for c in categories:
        a_tag = c.find("a")
        u, name = a_tag.get("href"), a_tag.get("title")
        if "(Earth-" in name:
            # Categories usually include items, locations etc. that are not characters.
            # Characters always include the universe they are from. (e.g. 'Earth-616').
            # Since we want only characters, we need to filter out the ones that are not characters.
            
            #characters_in_issue.append({"url": u, "name": name})
            characters_in_issue.append({"name": name})
    characters_in_issue = pd.DataFrame(characters_in_issue)
    return characters_in_issue
    
def clean_characters_names(characters : pd.DataFrame) -> pd.DataFrame:
    """
    Remove the word "Category:" from the name.
    Also removes the universe they're from, if it's 616, since that's the default universe.
    """
    characters["name"] = characters["name"].str.replace("Category:", "")
    characters["name"] = characters["name"].str.replace(" \(Earth-616\)", "", regex=True)
    #reminder: parenthesis are special characters in regex. They need to be escaped.
    
    return characters

def split_type_of_appearance(characters : pd.DataFrame) -> pd.DataFrame:
    """
    Makes a new column with the type of appearance, then removes it from the name.
    """
    # The expected input will be something like "Scott Summers/Appearance"
    # We split it at the '/'. The first half is the name, the second half is the kind of appearance.
    # The kind of appearance is then moved to the new column.
    
    # The last bit is the kind of appearance.
    characters["type of appearance"] = characters["name"].str.split("/").str[-1]
    # All the earlier bits (usually 1), will be the name.
    # We use str.join to join the bits back together, in case there's a '/' in the name itself.
    characters["name"] = characters["name"].str.split("/").str[0:-1].str.join("/")
    
    return characters

def group_characters_by_type_of_appearance(characters : pd.DataFrame, issue : str) -> pd.DataFrame:
    """
    Groups characters by type of appearance.
    Returns a dataframe with the type of appearance as columns and the names of the characters (in a list) as the values.
    """
    characters = characters.groupby("type of appearance")["name"].apply(list)
    # this is now a series. convert it to a dataframe so we can transpose it.
    characters = pd.DataFrame(characters)
    #now transpose
    characters = characters.transpose()
    # and add the issue to a new column
    characters['Issue'] = issue
    
    characters.set_index('Issue', inplace=True)
    
    return characters

def table_of_appearances_from_issue(issue_title:str ,issue_url:str) -> pd.DataFrame:
    """
    Runs the battery of functions.
    Returns the table of appearances for the issue.
    The first table is characters vs type of appearance.
    The second table has the issue as the index for the row,
        type of appearance as columns and list of names as values.
    """
    characters = list_characters_in_issue(issue_url)
    characters = clean_characters_names(characters)
    characters = split_type_of_appearance(characters)
    table_of_appearances = group_characters_by_type_of_appearance(characters, issue_title)
    return characters, table_of_appearances

def geometric_mean(*args):
    """
    Returns the geometric mean of a list of numbers.
    """
    return (math.prod(args))**(1./len(args))

def append_to_graph_table(character_table:pd.DataFrame, graph_table=pd.DataFrame(), weight_table=WEIGHTS_OF_APPEARANCES) -> pd.DataFrame:
    """
    Iterate through the table, find characters in the same issue and connect them in a new table.
    """
    connections = []
    for _, (c1, appearance1) in character_table[["name", "type of appearance"]].iterrows():
        for __, (c2, appearance2) in character_table[["name", "type of appearance"]].iterrows():            
            if c1 == c2:
                continue
            if not (appearance1 in weight_table and appearance2 in weight_table):
                continue
            weight = geometric_mean(weight_table[appearance1], weight_table[appearance2])
            connection = {"source":c1, "target":c2, "weight":weight}
            connections.append(connection)
    connections = pd.DataFrame(connections)
    graph_table = pd.concat([graph_table, connections])
            
    return graph_table

def sum_graph_table(graph_table:pd.DataFrame) -> pd.DataFrame:
    """Add all the weights of connections between the same characters."""
    # add the weights of the connections between the same characters
    relationship_df = graph_table.groupby(["source", "target"], sort=False, as_index=False).sum()
    # drop the rows with weight 0
    relationship_df = relationship_df[relationship_df["weight"] > 0]
    return relationship_df

def sort_graph_table_by_weight(graph_table:pd.DataFrame) -> pd.DataFrame:
    """Sort the graph table by weight, with the heaviest connections first."""
    return graph_table.sort_values(by="weight", ascending=False)


def build_list_of_issues_and_urls(titles_to_download:dict=TITLES_TO_DOWNLOAD):
    issues = []
    urls = []
    for title in TITLES_TO_DOWNLOAD:
        title, first_issue, last_issue = title["title"], title["first_issue"], title["last_issue"] 
        issues += create_list_of_issues("", title, first_issue, last_issue)
        urls += create_list_of_issue_urls_from_marvel_wiki(title, first_issue, last_issue)
    
    return {"issues": issues, "urls": urls}




if __name__ == "__main__":
    
    list_of_issues = build_list_of_issues_and_urls()
    issues, urls = list_of_issues["issues"], list_of_issues["urls"]
    
    graph_table = pd.DataFrame()
    table_of_appearances = pd.DataFrame()
    
    for i, (issue, url) in enumerate(tzip(issues, urls)):
        character_table, issue_table = table_of_appearances_from_issue(issue, url)
        graph_table = append_to_graph_table(character_table, graph_table)
        table_of_appearances = pd.concat([table_of_appearances, issue_table])
        if i % 10 == 0:    
            graph_table = sum_graph_table(graph_table)
            graph_table = sort_graph_table_by_weight(graph_table)
            
            graph_table.to_csv("./data/graph_table.csv", index=False)
            table_of_appearances.to_csv("./data/table_of_appearances.csv")
        
    graph_table = sum_graph_table(graph_table)  
    graph_table = sort_graph_table_by_weight(graph_table)
    
    graph_table.to_csv("./data/graph_table.csv", index=False)
    table_of_appearances.to_csv("./data/table_of_appearances.csv")
    
#%%

#%%