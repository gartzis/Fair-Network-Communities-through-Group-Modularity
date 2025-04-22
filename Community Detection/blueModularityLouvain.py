import sys
import os
import csv





sys.path.append('..\Algorithms')

from diversityFairness import diversityMetric
from modularityFairness import modularityFairnessMetric



from collections import defaultdict, deque

from networkx.utils import py_random_state
import networkx as nx
from networkx.algorithms.community.community_utils import is_partition
from networkx import NetworkXError
import pandas as pd

from networkx.algorithms.community import louvain_communities


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
def blueFairness_louvain_communities(
    G, weight="weight", resolution=1, threshold_mod=0.0000001,threshold_fmod=0.001, seed=None, node_attributes={},
):
    for u in G.nodes():
        G.nodes[u]['red_weight'] = 0
        G.nodes[u]['blue_weight'] = 0
        G.nodes[u]['inter_weight'] = 0
    
    for u,v in G.edges():
        G[u][v]['r_weight'] = 0
        G[u][v]['b_weight'] = 0  
        G[u][v]['inter_weight'] = 0

    for u,v in G.edges():
        
            
        if node_attributes[v] == 0 and node_attributes[u]==0: # red
            G[u][v]['r_weight'] = 1
            
            
            
        elif node_attributes[v] == 1 and node_attributes[u] ==1: # blue
            G[u][v]['b_weight'] = 1
        if node_attributes[v] != node_attributes[u]:
            G[u][v]['inter_weight'] = 1
            
            
        if  node_attributes[v] == 0: # red
            G.nodes[v]['red_weight'] +=1
        if node_attributes[u] == 0:        
            G.nodes[u]['red_weight'] +=1
        if  node_attributes[v] == 1: # blue
            G.nodes[v]['blue_weight'] +=1
        if node_attributes[u] == 1:
            G.nodes[u]['blue_weight'] +=1
        if node_attributes[v] != node_attributes[u]:
            G.nodes[u]['inter_weight'] +=1
            G.nodes[v]['inter_weight'] +=1

    d = blueFairness_louvain_partitions(G, weight, resolution, threshold_mod,threshold_fmod, seed, node_attributes=node_attributes)
    q = deque(d, maxlen=1)
    return q.pop()


@py_random_state("seed")
def blueFairness_louvain_partitions(
    G, weight="weight", resolution=1, threshold_mod=0.0000001,threshold_fmod=0.001, seed=None, node_attributes={},
):
    partition = [{u} for u in G.nodes()]
    
    if nx.is_empty(G):
        yield partition
        return
    mod,communityModularityist = modularityCustom(G, partition, resolution=resolution, weight=weight)
    diversityModularity,diversityModularityList, = diversityMetric(G, partition,G_attribute = node_attributes, resolution=resolution, weight=weight) 
    fmod, communityFairModularityist, fairnessModularityPercList_B,redModularityList,blueModularityList = modularityFairnessMetric(G, partition,G_attribute = node_attributes, resolution=resolution, weight=weight)
   
    


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
        
            
        if node_attributes[v] == 0 and node_attributes[u]==0: # red
            graph[u][v]['r_weight'] = 1
            
            
            
        elif node_attributes[v] == 1 and node_attributes[u] ==1: # blue
            graph[u][v]['b_weight'] = 1
        if node_attributes[v] != node_attributes[u]:
            graph[u][v]['inter_weight'] = 1
            
            
        if  node_attributes[v] == 0: # red
            graph.nodes[v]['red_weight'] +=1
        if node_attributes[u] == 0:        
            graph.nodes[u]['red_weight'] +=1
        if  node_attributes[v] == 1: # blue
            graph.nodes[v]['blue_weight'] +=1
        if node_attributes[u] == 1:
            graph.nodes[u]['blue_weight'] +=1
        if node_attributes[v] != node_attributes[u]:
            graph.nodes[u]['inter_weight'] +=1
            graph.nodes[v]['inter_weight'] +=1
            

            
                
            
            
                

    m = graph.size(weight="weight")
    
    graph = _gen_graph(graph, partition)
    iterationNum = 0
    
    partition, inner_partition, improvement = _one_level(
        graph,iterationNum,mod,fmod,communityFairModularityist,communityModularityist, m, partition, resolution, is_directed, seed, node_attributes=node_attributes)
    improvement = True
    iterationNum = 1
    
    
    
    
    

    while improvement:
        
        
        yield [s.copy() for s in partition]

        
        new_mod,communityModularityist = modularityCustom(
            G, partition, resolution=resolution, weight="weight"
        )
        inner_partition = list(inner_partition)
        diversityModularity,new_diversityModularityList, = diversityMetric(G, partition,G_attribute = node_attributes, resolution=resolution, weight=weight)
        new_fmod,new_communityFairModularityist,new_fairModPercList,new_redModularityList,new_blueModularityList = modularityFairnessMetric(G, partition,node_attributes, resolution=resolution, weight=weight) 
        
        sum_redModularityList = sum(redModularityList)
        sum_blueModularityList = sum(blueModularityList)
        




    
        
        check = new_mod - mod <= threshold_mod
        

        if check:
            return
        
        mod = new_mod
        fmod = new_fmod
        diversityModularityList = new_diversityModularityList
        redModularityList = new_redModularityList
        blueModularityList = new_blueModularityList 
        
        communityFairModularityist = new_communityFairModularityist
        fairModPercList = new_fairModPercList
        graph = _gen_graph(graph, inner_partition)
        
        
        partition, inner_partition, improvement = _one_level(
            graph,iterationNum,new_mod,new_fmod,communityFairModularityist,communityModularityist, m, partition, resolution, is_directed, seed, node_attributes=node_attributes)
        iterationNum += 1
       
        new_mod,communityModularityist = modularityCustom(
            G, partition, resolution=resolution, weight="weight"
        )
        
        




def _one_level(G,iterationNum,orig_mod,orig_fmod,communityModularityist,modList, m, partition, resolution=1, is_directed=False, seed=None, node_attributes={}):
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
    rand_nodes = list(G.nodes)
    seed.shuffle(rand_nodes)
    nb_moves = 1
    improvement = False
    iteNum = 0
    timesInWhile =0
    checkParameter = int(len(G.nodes())/2)
    
    while nb_moves > 0:
        if timesInWhile>checkParameter:
            break

        timesInWhile+=1
        iteNum += 1
        nb_moves = 0

        changes_foundNum = 0
        for u in rand_nodes:
            
            
            best_fair_gain = 0
            best_fair_remove_cost = 0

            new_fmod = orig_fmod
            new_best_mod = orig_mod

            best_gain = 0
            best_red_gain = 0
            best_blue_gain = 0
            gain_difference = 100
 
            best_fair_mod = new_fmod

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
                        Stot[best_com] * degree_r) / (2 * m**2)
                else:
                    remove_cost_R = degree_r / (2 * m**2)
                
                
                
                degree_b = degrees_b[u]
                
                Stot_b[best_com] -= degree_b
                
                
                    
                if iterationNum==0:
                    if node_attributes[u] == 0:
                            remove_cost_B = -((weights2comInter[best_com])) / (2*m) + resolution * (
                            (Stot_b[best_com]) * degree) / ((2 * m)**2)
                        
                        
                    else:
                        remove_cost_B = -((2*weights2comB[best_com]+weights2comInter[best_com])) / (2*m) + resolution * (
                            (Stot[best_com]+Stot_b[best_com]) * degree) / ((2 * m)**2)
                        
                else:
                
                    remove_cost_B = -((2*weights2comB[best_com]+weights2comInter[best_com])) / (2*m) + resolution * (
                            Stot[best_com]*degree_b+Stot_b[best_com] * degree) / ((2 * m)**2)
                
                

                fair_before_best_com = communityModularityist[best_com]
                
                
                
                

                
                
                
                fair_after_best_com = fair_before_best_com - (remove_cost_R-remove_cost_B)
            

            
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
                        - resolution * (Stot[nbr_com] * degree_r) / (2 * m**2)
                    )
                    
                    if iterationNum==0:
                        if node_attributes[u] == 0:
                            
                            gain_b = (
                            (wtInter) / (2*m)
                            - resolution * ((Stot_b[nbr_com]) * degree) / ((2 * m)**2)
                        )
                            
                            
                        else:
                            
                            gain_b = (
                            ((2*wtB)+wtInter) / (2*m)
                            - resolution * ((Stot[nbr_com]+Stot_b[nbr_com]) * degree) / ((2 * m)**2)
                        )
                            
                            
                    else:
                    
                    
                        gain_b = (
                            ((2*wtB)+wtInter) / (2*m)
                            - resolution * (Stot[nbr_com]*degree_b+Stot_b[nbr_com] * degree) / ((2 * m)**2)
                        )
                    
                    gain_rb = (wtInter / m) - resolution * ((Stot_r[nbr_com] * degree_b)+(Stot_b[nbr_com] * degree_r)) / (2 * m**2)

                    
                    
                
                
                fair_before_nbr_com = communityModularityist[nbr_com]
                
                
                
                fair_after_nbr_com = fair_before_nbr_com +(gain_r-gain_b)
                
                
               
                

                fair_gain = ((remove_cost_R+gain_r)-(remove_cost_B+gain_b))
                  
                
                new_fmod = best_fair_mod + fair_gain
                mod_gain = gain+remove_cost
                
                
                fair_before = abs(fair_before_nbr_com +fair_before_best_com)
                fair_after = abs(fair_after_nbr_com +fair_after_best_com)
                redmod_gain = remove_cost_R+gain_r
                bluemod_gain = remove_cost_B+gain_b
 

                
                
                check_in = redmod_gain>=best_red_gain and bluemod_gain>=best_blue_gain and redmod_gain-bluemod_gain<gain_difference
                check_in = abs(fair_after)<= abs(fair_before) and redmod_gain>=best_red_gain and bluemod_gain>=best_blue_gain
                
                
                check_in = mod_gain>best_gain and bluemod_gain>=best_blue_gain
                
                
               
                
                if check_in and nbr_com != node2com[u]:
                    
                    changes_foundNum+=1

                    best_fair_remove_cost = (remove_cost_R-remove_cost_B)
                    best_fair_gain = gain_r-gain_b
                    fair_before_nbr_com = fair_after_nbr_com
                    fair_before_best_com = fair_after_best_com
                    best_gain = mod_gain
                    best_red_gain = redmod_gain
                    best_blue_gain = bluemod_gain
                    gain_difference = redmod_gain-bluemod_gain
                    

                    best_com = nbr_com
                

            
            
                 
            

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
                       

                        
                        
                        communityModularityist[node2com[u]] = communityModularityist[node2com[u]] + best_fair_remove_cost
                        
                        communityModularityist[best_com] = communityModularityist[best_com] + best_fair_gain
                        
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

