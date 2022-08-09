from inspect import CO_OPTIMIZED
from utils import scrape, parse_issues, prepare_edges, process_appearances, visualization
from utils.ComicSeries import ComicSeries
import os
import pandas as pd
from dataclasses import dataclass

def make_graph_from_zero(series_to_scrape:list[ComicSeries], path:str="results", title:str="", scrape_from_wiki=True) -> None:
    """
    Runs the whole process from scratch.
    """
    if title == "": 
        title = f"{series_to_scrape[0].title} Vol {series_to_scrape[0].volume}" #default to title of first series in list
        assert len(title) > 0, "Title is empty." #shouldn't happen unless something really wrong happens    
    
    parent_path = os.path.join(path, title)
    data_path = os.path.join(parent_path, "data")
    output_path = os.path.join(parent_path, "output")
    
    # folder structure:
        # path/title
        #       - /data
        #       - /output
    
    if not scrape_from_wiki:
        appearances_per_issue = pd.read_csv(os.path.join(data_path, "table_of_appearances.csv"))
    else:    
        # make folder to save data and graphs, if it doesn't exist already
        create_directory_if_it_doesnt_exist(parent_path)
        create_directory_if_it_doesnt_exist(data_path)
        create_directory_if_it_doesnt_exist(output_path)
        
        # unpack issues from series
        issue_list = scrape.build_full_list_of_issues(series_to_scrape)
        
        # scrape each issue page and build table
        print("Scraping...")
        appearances_per_issue = parse_issues.build_full_table(issue_list, path=os.path.join(data_path, "table_of_appearances.csv"))
        # save table to csv
        appearances_per_issue.to_csv(os.path.join(data_path, "table_of_appearances.csv"), index=False)
    
    # get a quick summary of the table by characters:
    print("Counting appearances...")
    char_stats = process_appearances.count_types_of_appearances(appearances_per_issue)
    char_stats.to_csv(os.path.join(data_path, "character_stats.csv"), index=False)
    
    # drop the characters with too few appearances
    # filter:
    minimum_appearances = 2
    frequent_characters = char_stats[char_stats.Appearances >= minimum_appearances] # could be some other criteria
    # apply the filter:
    appearances_per_issue = appearances_per_issue[appearances_per_issue["character name"].isin(frequent_characters["character name"])]
    
    # calculate correlation matrix: 
    print("Calculating correlations...")
    weights = prepare_edges.build_weights_df(appearances_per_issue) # convert to numbers
    corr_matrix = prepare_edges.calculate_correlations(weights)
    
    # turn into edge list
    print("Listing edges...")
    edge_list = prepare_edges.build_edge_list(corr_matrix)
    edge_list.to_csv(os.path.join(data_path, "edge_list.csv"), index=False)
    
    # select/prune some edges/nodes
    print("Filtering edges...")
    edges_to_keep1 = prepare_edges.select_biggest_edges(edge_list)
    edges_to_keep2 = prepare_edges.select_edges_above_threshhold(edge_list, 0.5)
    edges_to_graph = pd.concat([edges_to_keep1, edges_to_keep2])   
    
    # convert to networkx graph object
    G = visualization.make_nx_graph(edges_to_graph)
    print("Partitionining graph into communities...")
    visualization.partition_communities(G) # partition into communities
    visualization.set_node_size(G, char_stats) # set node size
    
    # visualize graph with pyvis
    print("Building graph visualization...")
    visualization.show_graph(G, save_path=output_path, title=title)

def create_directory_if_it_doesnt_exist(path:str):
    if not os.path.exists(path):
        os.makedirs(path)
        
@dataclass
class SettingsToTweak:
    """This class is used to store settings for the program."""
    """Not currently used."""
    correlation_threshhold:float = 0.5
    desired_avg_edges_per_node:float = 3.0
    characters_to_keep_top_perc = 0.1
    characters_to_keep_min_appearances = 5
    weight_for_minor_appearances = 0.5
    weight_for_major_appearances = 1
    weight_for_mentions = 0.1
    
@dataclass
class Examples:
    savage_avengers = ComicSeries(title="Savage Avengers", volume=1, first_issue=1, last_issue=28)
    
    claremont_era = [
                      ComicSeries(title = "X-Men",         volume = 1, first_issue = 94, last_issue = 141),
                      ComicSeries(title = "Uncanny X-Men", volume = 1, first_issue = 142,last_issue = 280),
                      ComicSeries(title = "New Mutants",   volume = 1, first_issue = 1, last_issue  = 100),
                      ComicSeries(title = "X-Factor",      volume = 1, first_issue = 1, last_issue  = 70),
                      ComicSeries(title = "Excalibur",     volume = 1, first_issue = 1, last_issue  = 41),
                      ComicSeries(title = "X-Force",       volume = 1, first_issue = 1, last_issue  = 15),
                      ComicSeries(title = "Fallen Angels", volume = 1, first_issue = 1, last_issue  = 8),
                      ComicSeries(title = "X-Terminators", volume = 1, first_issue = 1, last_issue  = 4)]
    
    hickman_f4 = [
                  ComicSeries(title = "Fantastic Four", volume = 1, first_issue = 570, last_issue = 588),
                  ComicSeries(title = "FF",             volume = 1, first_issue = 1,   last_issue = 23),
                  ComicSeries(title = "Fantastic Four", volume = 1, first_issue = 600, last_issue = 611)]
    
    krakoa_era = [ComicSeries(title = "House of X",                      volume = 1, first_issue = 1, last_issue = 6),
                  ComicSeries(title = "Powers of X",                     volume = 1, first_issue = 1, last_issue = 6),
                  ComicSeries(title = "X-Men",                           volume = 5, first_issue = 1, last_issue = 21),
                  ComicSeries(title = "Marauders",                       volume = 1, first_issue = 1, last_issue = 27),
                  ComicSeries(title = "Excalibur",                       volume = 4, first_issue = 1, last_issue = 26),
                  ComicSeries(title = "New Mutants",                     volume = 4, first_issue = 1, last_issue = 24),
                  ComicSeries(title = "X-Force",                         volume = 6, first_issue = 1, last_issue = 26),
                  ComicSeries(title = "Fallen Angels",                   volume = 2, first_issue = 1, last_issue = 6),
                  ComicSeries(title = "Wolverine",                       volume = 7, first_issue = 1, last_issue = 19),
                  ComicSeries(title = "Cable",                           volume = 4, first_issue = 1, last_issue = 6),
                  ComicSeries(title = "Hellions",                        volume = 1, first_issue = 1, last_issue = 18),
                  ComicSeries(title = "X-Factor",                        volume = 1, first_issue = 1, last_issue = 10),
                  ComicSeries(title = "Empyre: X-Men",                   volume = 1, first_issue = 1, last_issue = 4),
                  ComicSeries(title = "Juggernaut",                      volume = 3, first_issue = 1, last_issue = 5),
                  ComicSeries(title = "X of Swords: Creation",           volume = 1, first_issue = 1, last_issue = 1),
                  ComicSeries(title = "X of Swords: Stasis",             volume = 1, first_issue = 1, last_issue = 1),
                  ComicSeries(title = "X of Swords: Destruction",        volume = 1, first_issue = 1, last_issue = 1),
                  ComicSeries(title = "S.W.O.R.D.",                      volume = 2, first_issue = 1, last_issue = 11),
                  ComicSeries(title = "Way of X",                        volume = 1, first_issue = 1, last_issue = 5),
                  ComicSeries(title = "X-Men",                           volume = 6, first_issue = 1, last_issue = 9),
                  ComicSeries(title = "X-Men: The Trial of Magneto",     volume = 1, first_issue = 1, last_issue = 5),
                  ComicSeries(title = "Inferno",                         volume = 2, first_issue = 1, last_issue = 4),
                  ComicSeries(title = "X Lives of Wolverine",            volume = 1, first_issue = 1, last_issue = 5),
                  ComicSeries(title = "X Deaths of Wolverine",           volume = 1, first_issue = 1, last_issue = 5),
                  ComicSeries(title = "Devil's Reign: X-Men",            volume = 1, first_issue = 1, last_issue = 3),
                  ComicSeries(title = "Planet-Size X-Men",               volume = 1, first_issue = 1, last_issue = 1),
                  ComicSeries(title = "X-Men: The Onslaught Revelation", volume = 1, first_issue = 1, last_issue = 1),
                  ComicSeries(title = "Cable: Reloaded",                 volume = 1, first_issue = 1, last_issue = 1),
                  ComicSeries(title = "Secret X-Men",                    volume = 1, first_issue = 1, last_issue = 1),
                  ComicSeries(title = "Immortal X-Men",                  volume = 1, first_issue = 1, last_issue = 4),
                  ComicSeries(title = "X-Men: Red",                      volume = 2, first_issue = 1, last_issue = 4),
                  ComicSeries(title = "Marauders",                       volume = 2, first_issue = 1, last_issue = 4),
                  ComicSeries(title = "Knights of X",                    volume = 1, first_issue = 1, last_issue = 3),
                  ComicSeries(title = "Legion of X",                     volume = 1, first_issue = 1, last_issue = 3),
                  ComicSeries(title = "Sabretooth",                      volume = 4, first_issue = 1, last_issue = 3)
                  ]
    
    
def main():
    examples = Examples()
    series_to_scrape = examples.krakoa_era
    #settings = SettingsToTweak()
    make_graph_from_zero(series_to_scrape, title="Krakoa Era", scrape_from_wiki=False)

if __name__ == "__main__":
    main()


