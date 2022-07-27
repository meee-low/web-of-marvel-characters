import networkx as nx
from pyvis.network import Network
from community import community_louvain
import pandas as pd
import datetime
import math

def make_nx_graph(pandas_edgelist:pd.DataFrame) -> nx.Graph:
    """
    Returns a networkx graph from a pandas dataframe of edges.
    """
    edge_list_copy = pandas_edgelist.copy()
    edge_list_copy.columns = ["source", "target", "weight"]
    G = nx.from_pandas_edgelist(edge_list_copy,
                                source = "source",
                                target = "target",
                                edge_attr = "weight",
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
    for character, number_of_appearances in zip(sizes['character name'], sizes['Appearances']):
        #sizes_dict[character] = math.log(max(number_of_appearances, 1), 10) * 13
        sizes_dict[character] = (number_of_appearances / 7) + 5
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
    set_size(G, size_key)
    partition_communities(G)

def show_graph(G: nx.Graph, notebook:bool=False, physics_buttons:bool=False) -> None:
    """
    Creates an html file of the graph using pyvis.
    """
    if notebook:
        net = Network(notebook = True, height="900px", width="1400px", bgcolor="#222222", font_color="white")
    else:
        net = Network(height="100%", width="100%", bgcolor="#222222", font_color="white")
    
    net.from_nx(G)

    nodes, edges = len(G.nodes()), len(G.edges())
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    
    if physics_buttons:
        net.show_buttons(filter_=['physics'])
        net.width = "70%"
    else:
        net.repulsion()
    net.show(f"output/X-Men_{timestamp}_n{nodes}-e{edges}.html")