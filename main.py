from dataclasses import dataclass
import os
from utils import scrape, parse_issues, prepare_edges, process_appearances, visualization
import pandas as pd

def make_graph_from_zero(issue_dict:dict, path:str=".", title:str="Avengers"):
    """
    Runs the whole process from scratch.
    """    
    # make folder to save data and graphs, if it doesn't exist already
    save_path = os.path.join(path, title)
    data_path = os.path.join(save_path, "data")
    output_path = os.path.join(save_path, "output")
    create_directory_if_it_doesnt_exist(save_path)
    create_directory_if_it_doesnt_exist(data_path)
    create_directory_if_it_doesnt_exist(output_path)
    # folder structure:
    # path/title
    #       - /data
    #       - /output
    
    # unpack issue dict
    issue_list = scrape.build_full_list_of_issues(issue_dict)
    
    # scrape each issue page and build table
    appearances_per_issue = parse_issues.build_full_table(issue_list)
    # save table to csv
    appearances_per_issue.to_csv(os.path.join(data_path, "table_of_appearances.csv"), index=False)
    
    # get a quick summary of the table by characters:
    char_stats = process_appearances.count_types_of_appearances(appearances_per_issue)
    char_stats.to_csv(os.path.join(data_path, "character_stats.csv"), index=False)
    
    # calculate correlation matrix: 
    # convert to numbers
    weights = prepare_edges.build_weights_df(appearances_per_issue)
    corr_matrix = prepare_edges.calculate_correlations(weights)
    
    # turn into edge list
    edge_list = prepare_edges.build_edge_list(corr_matrix)
    edge_list.to_csv(os.path.join(data_path, "edge_list.csv"), index=False)
    
    # select/prune some edges/nodes
    edges_to_keep1 = prepare_edges.select_biggest_edges(edge_list)
    edges_to_keep2 = prepare_edges.select_edges_above_threshhold(edge_list, 0.5)
    edges_to_graph = pd.concat([edges_to_keep1, edges_to_keep2])   
    
    # convert to networkx graph object
    G = visualization.make_nx_graph(edges_to_graph)
    visualization.partition_communities(G) # partition into communities
    # visualization.set_node_size(G, appearances_per_issue) # set node size
    
    # visualize graph with pyvis
    visualization.show_graph(G, save_path=output_path, title=title)

def create_directory_if_it_doesnt_exist(path:str):
    if not os.path.exists(path):
        os.makedirs(path)
        
@dataclass
class Settings:
    """This class is used to store settings for the program."""
    correlation_threshhold:float = 0.5
    desired_avg_edges_per_node:float = 3.0
    characters_to_keep_top_perc = 0.1
    characters_to_keep_min_appearances = 5
    weight_for_minor_appearances = 0.5
    weight_for_major_appearances = 1
    weight_for_mentions = 0.1
    
def main():
    issue_dict = [{"title": "Savage Avengers Vol 1", "first_issue": 1,  "last_issue": 28}]
    make_graph_from_zero(issue_dict, title="Savage Avengers")

if __name__ == "__main__":
    main()
    
