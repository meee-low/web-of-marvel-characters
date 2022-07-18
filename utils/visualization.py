import networkx as nx
from pyvis.network import Network
from community import community_louvain
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

def make_nx_graph(pandas_edgelist:pd.DataFrame) -> nx.Graph:
    """
    Returns a networkx graph from a pandas dataframe of edges.
    """
    G = nx.from_pandas_edgelist(pandas_edgelist,
                                source = "source",
                                target = "target",
                                edge_attr = "weight",
                                create_using = nx.Graph())
    return G

def trim_small_edges(G:nx.Graph, threshold:int) -> None:
    """Remove all the edges with weight less than threshold"""
    edges_to_remove = []
    for (a,b,attrs) in G.edges(data=True):
        if attrs['weight'] < threshold:
            edges_to_remove.append((a,b))
    G.remove_edges_from(edges_to_remove)
    
def only_keep_biggest_edges(G:nx.Graph) -> None:
    """
    Go through the edges and only keep the largest ones
    """
    edges_to_remove = []
    largest_weight = defaultdict(int)
    currently_largest_edges = defaultdict(list)
    for (source,target,attrs) in tqdm(G.edges(data=True)):
        if attrs['weight'] == largest_weight[source]:
            currently_largest_edges[source].append((source,target))
        elif attrs['weight'] > largest_weight[source]:
            # found a new largest weight
            for edge in currently_largest_edges[source]:
                # all the previous edges are irrelevant now
                edges_to_remove.append(edge)
            currently_largest_edges[source] = [(source,target)]
            largest_weight[source] = attrs['weight']
        else:
            #if attrs['weight'] < largest_weight[a]:
            edges_to_remove.append((source,target))
            
    G.remove_edges_from(edges_to_remove)
    
def trim_isolated_nodes(G):
    """
    Only keep the nodes that have at least 1 edge.
    """
    G.remove_nodes_from([n for n in G.nodes() if G.degree(n) == 0])

def set_size_attribute(G:nx.Graph, size_key:pd.DataFrame) -> None:
    """
    Set the size attribute of each node to the size of the character in the size_key.
    """
    sizes = size_key.loc[:, ['character name', 'Actual Appearances']].to_dict()
    nx.set_node_attributes(G, sizes, 'size')

def partition_communities(G:nx.Graph) -> None:
    """
    Makes a community partition of the graph using community_louvain.
    """
    communities = community_louvain.best_partition(G)
    nx.set_node_attributes(G, communities, 'group')
    
def clean_graph(G:nx.Graph, threshold:int, size_key:pd.DataFrame) -> None:
    """
    Battery of functions.
    """
    trim_small_edges(G, threshold)
    set_size_attribute(G, size_key)
    partition_communities(G)

def make_graph_html(G: nx.Graph, path:str) -> None:
    """
    Creates an html file of the graph using pyvis.
    """
    #node_degree = nx.degree(G)
    net = Network(height="100%", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    net.show_buttons(filter_=['physics'])
    net.repulsion()
    net.show(path)