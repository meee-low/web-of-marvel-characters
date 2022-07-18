import graph, parse_issues, process_appearances, scrape, visualization
import pandas as pd

def main():
    table = pd.read_csv("./data/table_of_appearances.csv")
    
    edge_list = pd.read_csv("./data/full_edge_list.csv")
    #char_stats = pd.read_csv("./data/char_stats.csv")
     
    G = visualization.make_nx_graph(edge_list)
    visualization.partition_communities(G)
    #visualization.trim_small_edges(G, 15*100)
    visualization.only_keep_biggest_edges(G)
    visualization.trim_isolated_nodes(G)
    visualization.make_graph_html(G, "onlybiggest.html")

def build_full_database_of_issues():
    """
    Build a database of all the issues in the database.
    """
    issues = scrape.build_full_list_of_issues()

def build_full_weights_and_edges(table:pd.DataFrame):
    weights = graph.build_weights_df(table)
    weights.to_csv("./data/full_weights.csv")
    
    edge_list = graph.build_edge_list(weights)
    edge_list.to_csv("./data/full_edge_list.csv")
    
def build_trimmed_weights_and_edges(table:pd.DataFrame):
    """
    
    """
    char_stats = process_appearances.count_types_of_appearances(table)
    char_stats.to_csv("./data/char_stats.csv")
    
    table = process_appearances.drop_less_relevant_characters(table, char_stats, "Appearances", 1)
    table = process_appearances.drop_less_relevant_characters(table, char_stats, "Appearances", 15)
    
    weights = graph.build_weights_df(table)
    weights.to_csv("./data/trimmed_weights.csv")
    
    edge_list = graph.build_edge_list(weights)
    edge_list.to_csv("./data/trimmed_edge_list.csv")
    
if __name__ == "__main__":
    main()