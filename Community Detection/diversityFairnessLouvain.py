import sys
import os
import csv





sys.path.append('..\Algorithms')

from diversityFairness import diversityMetric



from collections import defaultdict, deque

from networkx.utils import py_random_state
import networkx as nx
from networkx.algorithms.community.community_utils import is_partition
from networkx import NetworkXError


class NotAPartition(NetworkXError):
    """Raised if a given collection is not a partition."""

    def __init__(self, G, collection):
        msg = f"{collection} is not a valid partition of the graph {G}"
        super().__init__(msg)



def modularityCustom(G, communities, weight="weight", resolution=1):

    if not isinstance(communities, list):
        communities = list(communities)
    if not is_partition(G, communities):
        raise NotAPartition(G, communities)

    directed = G.is_directed()
    if directed:
        out_degree = dict(G.out_degree(weight=weight))
        in_degree = dict(G.in_degree(weight=weight))
        m = sum(out_degree.values())
        norm = 1 / m**2
    else:
        out_degree = in_degree = dict(G.degree(weight=weight))
        deg_sum = sum(out_degree.values())
        m = deg_sum / 2
        norm = 1 / deg_sum**2

    def community_contribution(community):
        comm = set(community)
        L_c = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm)

        out_degree_sum = sum(out_degree[u] for u in comm)
        in_degree_sum = sum(in_degree[u] for u in comm) if directed else out_degree_sum

        return L_c / m - resolution * out_degree_sum * in_degree_sum * norm
    communityModularityist = []
    for community in communities:
        community_contribution(community)
        communityModularityist.append(community_contribution(community))

    return sum(map(community_contribution, communities)),communityModularityist




@py_random_state("seed")
def diversityFairness_louvain_communities(
    G, weight="weight", resolution=1, threshold_mod=0.0000001,threshold_fmod=0.001, seed=None, node_attributes={},
):
    

    d = diversityFairness_louvain_partitions(G, weight, resolution, threshold_mod,threshold_fmod, seed, node_attributes=node_attributes)
    q = deque(d, maxlen=1)
    return q.pop()


@py_random_state("seed")
def diversityFairness_louvain_partitions(
    G, weight="weight", resolution=1, threshold_mod=0.0000001,threshold_fmod=0.001, seed=None, node_attributes={},
):
    partition = [{u} for u in G.nodes()]
    
    if nx.is_empty(G):
        yield partition
        return
    
    
    is_directed = G.is_directed()
        
    if G.is_multigraph():
        graph = _convert_multigraph(G, weight, is_directed)
    else:
        graph = G.__class__()
        graph.add_nodes_from(G)
        graph.add_weighted_edges_from(G.edges(data=weight, default=1))
        # Add the edge attributes for the red and blue weights
        
                
        # Add the node attributes for the red and blue weights
        for u in graph.nodes():
            graph.nodes[u]['red_weight'] = 0
            graph.nodes[u]['blue_weight'] = 0
            graph.nodes[u]['inter_weight'] = 0
        for u,v in graph.edges():
            graph[u][v]['r_weight'] = 0
            graph[u][v]['b_weight'] = 0
            graph[u][v]['inter_weight'] = 0  
            
        
        for u,v in graph.edges():
            if node_attributes[u] == 0 or node_attributes[v] == 0: # If either node is red
                graph[u][v]['r_weight'] = 1
                graph[u][v]['b_weight'] = 0

                
            elif node_attributes[u] == 1 or node_attributes[v] == 1: # If either node is blue
                graph[u][v]['b_weight'] = 1
                graph[u][v]['r_weight'] = 0

            if node_attributes[u] != node_attributes[v]:
                graph[u][v]['inter_weight'] = 1
                

            if node_attributes[v] == 0 :
                graph.nodes[u]['red_weight'] +=1
            if node_attributes[u] == 0:
                graph.nodes[v]['red_weight'] +=1
            if node_attributes[v] == 1:
                graph.nodes[u]['blue_weight'] +=1
            if node_attributes[u] == 1:
                graph.nodes[v]['blue_weight'] +=1
            if node_attributes[v] != node_attributes[u]:
                graph.nodes[u]['inter_weight'] +=1
                graph.nodes[v]['inter_weight'] +=1
                
                
                
            

    mod,communityModularityist = modularityCustom(G, partition, resolution=resolution, weight=weight)
    diversityModularity,diversityModularityList, = diversityMetric(G, partition,G_attribute = node_attributes, resolution=resolution, weight=weight) 
   
    



            
                
            
            
                

    m = graph.size(weight="weight")
    
    
    graph = _gen_graph(graph, partition)
    iterationNum = 0
    # Count the number of neighbors with r_weight equal to 1 for each node
    r_weight_neighbors_count = {}
    for node in graph.nodes():
        r_weight_neighbors_count[node] = sum(1 for neighbor in graph.neighbors(node) if graph[node][neighbor].get('inter_weight') == 1)

    # Sort nodes based on the number of neighbors with r_weight equal to 1
    sorted_nodes = sorted(graph.nodes(), key=lambda node: r_weight_neighbors_count[node], reverse=True)
    nodesList = list(sorted_nodes)
    

    partition, inner_partition, improvement = _one_level(
        graph,iterationNum,mod,diversityModularityList,communityModularityist, m, partition,nodesList, resolution, is_directed, seed, node_attributes=node_attributes)
    improvement = True
    iterationNum = 1
    





    while improvement:

        # gh-5901 protect the sets in the yielded list from further manipulation here
        yield [s.copy() for s in partition]

        

        new_mod,communityModularityist = modularityCustom(
            graph, inner_partition, resolution=resolution, weight="weight"
        )
        inner_partition = list(inner_partition)
        diversityModularity,new_diversityModularityList, = diversityMetric(G, partition,G_attribute = node_attributes, resolution=resolution, weight=weight) 
      
        

        


    
        
        check = new_mod - mod <= threshold_mod

        if check:
            return
        mod = new_mod

        
        
        diversityModularityList = new_diversityModularityList

        
        graph = _gen_graph(graph, inner_partition)
        
        r_weight_neighbors_count = {}
        for node in graph.nodes():
            r_weight_neighbors_count[node] = sum(1 for neighbor in graph.neighbors(node) if graph[node][neighbor].get('inter_weight') == 1)

        # Sort nodes based on the number of neighbors with r_weight equal to 1
        sorted_nodes = sorted(graph.nodes(), key=lambda node: r_weight_neighbors_count[node], reverse=True)
        nodesList = list(sorted_nodes)
        
        partition, inner_partition, improvement = _one_level(
            graph,iterationNum,new_mod,new_diversityModularityList,communityModularityist, m, partition,nodesList, resolution, is_directed, seed, node_attributes=node_attributes)
        iterationNum += 1
        




def _one_level(G,iterationNum,orig_mod,diversityModularityList,modList, m, partition,nodesList, resolution=1, is_directed=False, seed=None, node_attributes={}):
    """Calculate one level of the Louvain partitions tree

    Parameters
    ----------
    G : NetworkX Graph/DiGraph
        The graph from which to detect communities
    m : number
        The size of the graph `G`.
    partition : list of sets of nodes
        A valid partition of the graph `G`
    resolution : positive number
        The resolution parameter for computing the modularity of a partition
    is_directed : bool
        True if `G` is a directed graph.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    """
 

        
        
        
        
    
    node2com = {u: i for i, u in enumerate(G.nodes())}
    
    inner_partition = [{u} for u in G.nodes()]
    if is_directed:
        in_degrees = dict(G.in_degree(weight="weight"))
        out_degrees = dict(G.out_degree(weight="weight"))
        Stot_in = list(in_degrees.values())
        Stot_out = list(out_degrees.values())
        # Calculate weights for both in and out neighbours without considering self-loops
        nbrs = {}
        for u in G:
            nbrs[u] = defaultdict(float)
            for _, n, wt in G.out_edges(u, data="weight"):
                if u != n:
                    nbrs[u][n] += wt
            for n, _, wt in G.in_edges(u, data="weight"):
                if u != n:
                    nbrs[u][n] += wt
    else:
        degrees = dict(G.degree(weight="weight"))
        Stot = list(degrees.values())
        nbrs = {u: {v: data["weight"] for v, data in G[u].items() if v != u} for u in G}



        degrees_r = dict(G.nodes(data="red_weight"))

        
            
        Stot_r = list(degrees_r.values())
        nbrs_r = {u: {v: data["r_weight"] for v, data in G[u].items() if v != u} for u in G}

        degrees_b = dict(G.nodes(data="blue_weight"))

        Stot_b = list(degrees_b.values()) 
        nbrs_b = {u: {v: data["b_weight"] for v, data in G[u].items() if v != u} for u in G}
        nbrs_inter = {u:{v:data["inter_weight"] for v, data in G[u].items() if v != u} for u in G}

    rand_nodes = nodesList
    nb_moves = 1
    improvement = False
    iteNum = 0
    timesInWhile = 0
    checkParameter = int(len(G.nodes())/2)
    
    while nb_moves > 0:
        if timesInWhile>checkParameter:
            break
        
        timesInWhile += 1
        
        iteNum += 1
        nb_moves = 0

        changes_foundNum = 0
        for u in rand_nodes:
            
            best_fair_gain = 0
            best_fair_remove_cost = 0

            

            best_gain = 0
            best_diversity = 0
 
           

            best_com = node2com[u]
            weights2com = _neighbor_weights(nbrs[u], node2com)
            weights2comR = _neighbor_weights(nbrs_r[u], node2com)
            weights2comB = _neighbor_weights(nbrs_b[u], node2com)
            weights2comInter = _neighbor_weights(nbrs_inter[u], node2com)

            if is_directed:
                in_degree = in_degrees[u]
                out_degree = out_degrees[u]
                Stot_in[best_com] -= in_degree
                Stot_out[best_com] -= out_degree
                remove_cost = (
                    -weights2com[best_com] / m
                    + resolution
                    * (out_degree * Stot_in[best_com] + in_degree * Stot_out[best_com])
                    / m**2
                )
            else:

                
                
                

                
                degree = degrees[u]
                Stot[best_com] -= degree
                remove_cost = -weights2com[best_com] / m + resolution * (
                    Stot[best_com] * degree
                ) / (2 * m**2)

                degree_r = degrees_r[u]
                Stot_r[best_com] -= degree_r
                
                if iterationNum>0:
                    remove_cost_R = -weights2comR[best_com] / m + resolution * (
                        Stot_r[best_com] * degree_r) / (2 * m**2)
                else:
                    remove_cost_R = degree_r / (2 * m**2)
                
                
                
                degree_b = degrees_b[u]
                
                Stot_b[best_com] -= degree_b
                
                if iterationNum>0:
                    
                    remove_cost_B = -weights2comB[best_com] / m + resolution * (
                        Stot_b[best_com] * degree_b) / (2 * m**2)
                else:
                    remove_cost_B = degree_b / (2 * m**2)
                

                
                
                diversityModularity_before_best_com = diversityModularityList[best_com]
                remove_cost_inter = -weights2comInter[best_com] / m + resolution * ((Stot_r[best_com] * degree_b)+(Stot_b[best_com] * degree_r)) / (2 * m**2)
                
                
                
                diversityModularity_after_best_com = diversityModularity_before_best_com + remove_cost_inter
                

                
                
                
                

            
            for nbr_com, wt in weights2com.items():
                if is_directed:
                    gain = (
                        remove_cost
                        + wt / m
                        - resolution
                        * (
                            out_degree * Stot_in[nbr_com]
                            + in_degree * Stot_out[nbr_com]
                        )
                        / m**2
                    )
                else:
                    wtR = weights2comR[nbr_com]
                    wtB = weights2comB[nbr_com]
                    wtInter = weights2comInter[nbr_com]
                    gain = (
                        remove_cost
                        + wt / m
                        - resolution * (Stot[nbr_com] * degree) / (2 * m**2)
                    )
                    
                    gain = (
                        wt / m
                        - resolution * (Stot[nbr_com] * degree) / (2 * m**2)
                    )

                    
                    
                    gain_r = (
                         wtR / m
                        - resolution * (Stot_r[nbr_com] * degree_r) / (2 * m**2)
                    )
                    
                    gain_b = (
                         wtB / m
                        - resolution * (Stot_b[nbr_com] * degree_b) / (2 * m**2)
                    )
                    
                    gain_rb = (wtInter / m) - resolution * ((Stot_r[nbr_com] * degree_b)+(Stot_b[nbr_com] * degree_r)) / (2 * m**2)

                    
                    
                
                
                
                
                
                
                diversityModularity_before_nbr_com = diversityModularityList[nbr_com]
                
                

                diversityModularity_after_nbr_com = diversityModularity_before_nbr_com + gain_rb
                
                fair_Inter_before = abs(diversityModularity_before_nbr_com +diversityModularity_before_best_com)
                fair_Inter_after = abs(diversityModularity_after_nbr_com +diversityModularity_after_best_com)
               
                

                mod_gain = gain+remove_cost
                diversity_gain = gain_rb+ remove_cost_inter
                check_in = abs(fair_Inter_after)- abs(fair_Inter_before)
                check_in = best_diversity<=diversity_gain and mod_gain>best_gain
                    
               
                
                if check_in and nbr_com != node2com[u]:
                    changes_foundNum+=1


                    best_com = nbr_com
                    best_diversity = diversity_gain
                    best_gain = mod_gain
                

            
            
                 
            

            check = True
            if check:
            
                
                 
                if is_directed:
                    Stot_in[best_com] += in_degree
                    Stot_out[best_com] += out_degree
                else:
                    Stot[best_com] += degree
                    Stot_r[best_com] += degree_r
                    Stot_b[best_com] += degree_b
                
                if best_com != node2com[u] and best_gain>=0:
                    

                    connectedBool = True


                    if connectedBool:
                       

                        
                        
                        com = G.nodes[u].get("nodes", {u})
                        
                        partition[node2com[u]].difference_update(com)
                        inner_partition[node2com[u]].remove(u)
                        partition[best_com].update(com)
                        inner_partition[best_com].add(u)
                        improvement = True
                        nb_moves += 1
                        node2com[u] = best_com
               
    
    partition = list(filter(len, partition))
    inner_partition = list(filter(len, inner_partition))
    return partition, inner_partition, improvement


def _neighbor_weights(nbrs, node2com):
    """Calculate weights between node and its neighbor communities.

    Parameters
    ----------
    nbrs : dictionary
           Dictionary with nodes' neighbours as keys and their edge weight as value.
    node2com : dictionary
           Dictionary with all graph's nodes as keys and their community index as value.

    """
    weights = defaultdict(float)
    for nbr, wt in nbrs.items():
        weights[node2com[nbr]] += wt

    return weights


def _gen_graph(G, partition):
    
    """Generate a new graph based on the partitions of a given graph"""
    H = G.__class__()
    node2com = {}
    for i, part in enumerate(partition):
        nodes = set()
        red_degree = 0
        blue_degree = 0
        inter_degree = 0
        for node in part:
            node2com[node] = i
            red_degree +=G.nodes[node]['red_weight']
            blue_degree +=G.nodes[node]['blue_weight']
            inter_degree += G.nodes[node]['inter_weight']
            
            
            
            nodes.update(G.nodes[node].get("nodes", {node}))
        H.add_node(i, red_weight= 0, blue_weight = 0, inter_weight= 0)

        temp_red = H.nodes[i]["red_weight"]
        temp_blue = H.nodes[i]["blue_weight"]
        temp_inter = H.nodes[i]["inter_weight"]
        
        H.add_node(i, nodes=nodes, red_weight=red_degree+temp_red, blue_weight=blue_degree+temp_blue, inter_weight=inter_degree+temp_inter)
        

    for node1, node2, weights in G.edges(data=True):
        wt = weights["weight"]
        wt_red = weights["r_weight"]
        wt_blue = weights["b_weight"]
        wt_inter = weights['inter_weight']
        com1 = node2com[node1]
        com2 = node2com[node2]
        temp = H.get_edge_data(com1, com2, {"weight": 0})["weight"]
        temp_red = H.get_edge_data(com1, com2, {"r_weight": 0})["r_weight"]
        temp_blue = H.get_edge_data(com1, com2, {"b_weight": 0})["b_weight"]
        temp_inter = H.get_edge_data(com1, com2, {"inter_weight":0})["inter_weight"]
        H.add_edge(com1, com2, weight=wt +temp, r_weight=wt_red+temp_red, b_weight=wt_blue+temp_blue, inter_weight=wt_inter+temp_inter)

    return H


def _convert_multigraph(G, weight, is_directed):
    """Convert a Multigraph to normal Graph"""
    if is_directed:
        H = nx.DiGraph()
    else:
        H = nx.Graph()
    H.add_nodes_from(G)
    for u, v, wt in G.edges(data=weight, default=1):
        if H.has_edge(u, v):
            H[u][v]["weight"] += wt
        else:
            H.add_edge(u, v, weight=wt)
    return H