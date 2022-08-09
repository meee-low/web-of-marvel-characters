import networkx as nx
from pyvis.network import Network
from community import community_louvain
import pandas as pd
import datetime
import math
import os

def make_nx_graph(pandas_edgelist:pd.DataFrame) -> nx.Graph:
    """
    Returns a networkx graph from a pandas dataframe of edges.
    """
    edge_list_copy = pandas_edgelist.copy()
    edge_list_copy.columns = ["source", "target", "weight"]
    
    min_weight = edge_list_copy["weight"].min()
    max_weight = edge_list_copy["weight"].max()
    desired_max_width = 10
    desired_min_width = 0.5
    
    lin_scale = lambda x: linear_scale(x, min_weight, max_weight, desired_min_width, desired_max_width)
    
    edge_list_copy["width"] = edge_list_copy["weight"].apply(lin_scale) # scale up the weight
    G = nx.from_pandas_edgelist(edge_list_copy,
                                source = "source",
                                target = "target",
                                edge_attr = ["weight", "width"],
                                create_using = nx.Graph())
    return G

def trim_isolated_nodes(G):
    """
    Only keep the nodes that have at least 1 edge.
    """
    G.remove_nodes_from([n for n in G.nodes() if G.degree(n) == 0])

def set_node_size(G:nx.Graph, size_key:pd.DataFrame) -> None:
    """
    Set the size attribute of each node to the size of the character in the size_key.
    """
    sizes = size_key.to_dict("list")
    sizes_dict = {}
    
    #note: this should be scaled dynamically, based on the max and min number of appearances for the characters
    # maximum should have a size of around 35, minimum should have a size of around 5
    # scale linearly between the two
    
    min_number_of_appearances = size_key["Appearances"].min()
    max_number_of_appearances = size_key["Appearances"].max()
    desired_max_size = 35
    desired_min_size = 5
    
    for character, number_of_appearances in zip(sizes['character name'], sizes['Appearances']):
        sizes_dict[character] = linear_scale(number_of_appearances, min_number_of_appearances, max_number_of_appearances, desired_min_size, desired_max_size)
    nx.set_node_attributes(G, sizes_dict, 'size')

def partition_communities(G:nx.Graph) -> None:
    """
    Makes a community partition of the graph using community_louvain.
    """
    communities = community_louvain.best_partition(G)
    nx.set_node_attributes(G, communities, 'group')
    
def set_graph_attributes(G:nx.Graph, size_key:pd.DataFrame) -> None:
    """
    Battery of functions.
    """
    set_node_size(G, size_key)
    partition_communities(G)

def show_graph(G: nx.Graph, notebook:bool=False, physics_buttons:bool=False, title:str = "X-Men", save_path:str="output-test/") -> None:
    """
    Creates an html file of the graph using pyvis.
    """
    if notebook:
        net = Network(notebook = True, height="900px", width="1400px", bgcolor="#222222", font_color="white")
    else:
        net = Network(height="100%", width="100%", bgcolor="#222222", font_color="white")
    
    net.from_nx(G)

    if physics_buttons:
        net.show_buttons(filter_=['physics'])
        net.width = "70%"
    else:
        net.repulsion()
        
    nodes, edges = len(G.nodes()), len(G.edges())
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    file_path = os.path.join(save_path, f"{title}_{timestamp}_n{nodes}-e{edges}.html")
    net.show(file_path)
    
    
def linear_scale(x, min_x, max_x, min_y, max_y):
    """
    Linear scale.
    
    From:     
    y = a(x-offset) + b
    
    a = (max_y - min_y) / (max_x - min_x)
    b = min_y
    offset = min_x
    """
    return ((max_y - min_y) / (max_x - min_x)) * (x - min_x) + min_y