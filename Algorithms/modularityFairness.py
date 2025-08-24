"""Modularity fairness metrics.

This module measures the difference between group-aware modularities inside
communities for graphs with a binary node attribute. It exposes utilities to
populate the auxiliary attributes and to evaluate a partition.
"""

import networkx as nx
import pandas as pd



def compute_modularityFairness(G, communities, weight="weight", resolution=1):
    """Compute fairness signals from red/blue-aware modularities.

    For each community, compute red-favoring and blue-favoring modularities by
    counting intra-community red-only/blue-only edges (with inter edges counted
    once for each). The null-model terms are formed using the total red/blue
    degrees within the community. The function returns the difference
    (modularityR - modularityB) per community, a normalized difference with
    respect to standard modularity, and the individual red/blue modularities.

    Args:
        G: NetworkX Graph with auxiliary attributes set by
           ``modularityFairnessMetric``.
        communities: Iterable of node sets/lists representing a partition.
        weight: Base edge weight attribute (default: "weight").
        resolution: Resolution parameter for null-model terms.

    Returns:
        (sum_diff, per_comm_diff_list, per_comm_norm_diff_list,
         per_comm_red_mod_list, per_comm_blue_mod_list)
    """
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



        degrees_red = dict(G.nodes(data="red_weight"))
        degrees_blue = dict(G.nodes(data="blue_weight"))

    def community_contribution(community):
        
        if len(community)>0:
            
            comm = set(community)

            out_degree_sum = sum(out_degree[u] for u in comm)
            degree_R = sum(degrees_red[u] for u in comm)
            degree_B = sum(degrees_blue[u] for u in comm)

            L_c = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm)


            inter_L =sum(wt for u, v, wt in G.edges(comm, data="inter_weight", default=1) if v in comm)
     
            
            fair_L_cR = 2*sum(wt for u, v, wt in G.edges(comm, data="r_weight", default=1) if v in comm)+ inter_L
            fair_L_cB = 2*sum(wt for u, v, wt in G.edges(comm, data="b_weight", default=1) if v in comm) + inter_L
            
            in_degree_sum = sum(in_degree[u] for u in comm) if directed else out_degree_sum
            


            modularityR = (fair_L_cR / (2*m)) - (resolution * out_degree_sum * degree_R * norm)

            modularityB = (fair_L_cB / (2*m)) - (resolution * out_degree_sum * degree_B * norm)

            
            modularityCommunity = (L_c / m) - (resolution * out_degree_sum * in_degree_sum * norm)
            if modularityCommunity !=0:
                fairModPerc = (modularityR-modularityB)/abs(modularityCommunity)
            else:
                fairModPerc = 0

            modularityInter = (inter_L / m) - (resolution * degree_R * degree_B * norm)
           

            return (modularityR-modularityB),fairModPerc,modularityR,modularityB

        else:
            return 0
    communitiesNum = 0
    for c in communities:
        if len(c)>0:
            communitiesNum+=1

    communityModularityist = []
    
    fairModPercList = []
    redModularityList = []
    blueModularityList = []

    
    for community in communities:
        community_cont = community_contribution(community)
        communityModularityist.append(community_cont[0])
        fairModPercList.append(community_cont[1])
        redModularityList.append(community_cont[2])
        blueModularityList.append(community_cont[3])
        
        
        
    return sum(communityModularityist),communityModularityist,fairModPercList,redModularityList,blueModularityList


def modularityFairnessMetric(G, communities,G_attribute, weight="weight", resolution=1):
    """Populate attributes and compute modularity fairness for a partition.

    Derives edge-level indicators (r_weight, b_weight, inter_weight) and
    per-node degree counts (red_weight, blue_weight) from the binary attribute
    mapping. Then evaluates the partition with ``compute_modularityFairness``.

    Args:
        G: NetworkX Graph to annotate and evaluate.
        communities: Partition as an iterable of node sets/lists.
        G_attribute: Dict mapping node -> {0,1} group label.
        weight: Base edge weight attribute (default: "weight").
        resolution: Resolution parameter for the null model.

    Returns:
        (sum_diff, per_comm_diff_list, per_comm_norm_diff_list,
         per_comm_red_mod_list, per_comm_blue_mod_list)
    """
    
    for u in G.nodes():
        G.nodes[u]['red_weight'] = 0
        G.nodes[u]['blue_weight'] = 0
        
    
    for u,v in G.edges():
        G[u][v]['r_weight'] = 0
        G[u][v]['b_weight'] = 0  
        G[u][v]['inter_weight'] = 0
        G[u][v]['redblue_weight'] = 0
        G[u][v]['bluered_weight'] = 0

    for u,v in G.edges():
        if G_attribute[u] == 0 and G_attribute[v]==0: # red
            G[u][v]['r_weight'] = 1
            
            
            
        if G_attribute[u] == 1 and G_attribute[v]==1: # blue
            G[u][v]['b_weight'] = 1

        if G_attribute[u] != G_attribute[v]:
            G[u][v]['redblue_weight'] = 1
            G[u][v]['bluered_weight'] = 1
            G[u][v]['inter_weight'] = 1

            
            
        if  G_attribute[v] == 0: # red
            G.nodes[v]['red_weight'] +=1
        if G_attribute[u] == 0:        
            G.nodes[u]['red_weight'] +=1
        if  G_attribute[v] == 1: # blue
            G.nodes[v]['blue_weight'] +=1
        if G_attribute[u] == 1:
            G.nodes[u]['blue_weight'] +=1

            
    fairModularity,fairModularityList,fairModularityPerc,redModularityList,blueModularityList = compute_modularityFairness(G, communities, weight="weight", resolution=1)
    
    return fairModularity,fairModularityList,fairModularityPerc,redModularityList,blueModularityList
    
    