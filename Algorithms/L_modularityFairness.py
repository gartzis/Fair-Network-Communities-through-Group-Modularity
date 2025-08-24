"""L-modularity fairness metrics.

This module computes a fairness-aware difference between group modularities for
partitions over graphs with a binary attribute. The L-variant separates the
red-only, blue-only, and inter-group contributions and uses corresponding
normalization constants to form the null-model terms. Utilities are provided to
populate temporary weights and to evaluate a partition.
"""

import networkx as nx
import pandas as pd



def compute_LmodularityFairness(G, communities, weight="weight", resolution=1):
    """Compute L-modularity fairness signals for a partition.

    For each community, this function computes:
      - modularityR: fairness-aware modularity favoring the red group
      - modularityB: fairness-aware modularity favoring the blue group
      - fairModPerc: normalized difference (modularityR - modularityB) divided
        by the absolute standard modularity of the same community (when nonzero)

    The inter-, red-only, and blue-only edge masses inside communities are
    combined with null-model expectations that rely on corresponding degree
    totals and L-specific normalizations.

    Args:
        G: NetworkX Graph with temporary attributes set (see
           ``LModularityFairnessMetric``).
        communities: Iterable of node sets/lists representing a partition of G.
        weight: Edge attribute to use as base weight (default: "weight").
        resolution: Resolution parameter for null-model terms.

    Returns:
        A tuple:
        (sum_diff, per_comm_diff_list, per_comm_norm_diff_list,
         per_comm_red_mod_list, per_comm_blue_mod_list)
        where ``sum_diff = sum(modularityR - modularityB)`` over communities.
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
        deg_sumR = sum(wt for u, v, wt in G.edges( data="r_weight", default=1))
        mR = deg_sumR
        if deg_sumR !=0:

            normR = 1 / (deg_sumR*4*m)
        else:
            normR = 1
        deg_sumB = sum(wt for u, v, wt in G.edges( data="b_weight", default=1))
        mB = deg_sumB 
        if deg_sumB !=0:
            normB = 1 / (deg_sumB*4*m)
        else:
            normB = 1

        
        deg_sumInter = sum(wt for u, v, wt in G.edges( data="inter_weight", default=1))
        mInter = deg_sumInter
        if deg_sumInter !=0:
            normInter = 1 / (mInter*2*m)
        else:
            normInter = 1



        degrees_red = dict(G.nodes(data="red_weight"))
        degrees_blue = dict(G.nodes(data="blue_weight"))
        red_nodes_degrees_blue = dict(G.nodes(data="red_node_blue_weight"))
        blue_nodes_degrees_red = dict(G.nodes(data="blue_node_red_weight"))
        degrees_inter = dict(G.nodes(data="inter_weight"))

    def community_contribution(community):
        
        if len(community)>0:
            comm = set(community)

            out_degree_sum = sum(out_degree[u] for u in comm)
            degree_R = sum(degrees_red[u] for u in comm)
            degree_B = sum(degrees_blue[u] for u in comm)
            red_node_blue_degree = sum(red_nodes_degrees_blue[u] for u in comm)
            blue_node_red_degree = sum(blue_nodes_degrees_red[u] for u in comm)
            degree_inter = sum(degrees_inter[u] for u in comm)

            L_c = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm)

            fair_L_cR = sum(wt for u, v, wt in G.edges(comm, data="r_weight", default=1) if v in comm)
            fair_L_cB = sum(wt for u, v, wt in G.edges(comm, data="b_weight", default=1) if v in comm)
            inter_L =sum(wt for u, v, wt in G.edges(comm, data="inter_weight", default=1) if v in comm)
            
                       
            in_degree_sum = sum(in_degree[u] for u in comm) if directed else out_degree_sum


        
            

            modularityR = (fair_L_cR / m)+ (inter_L/(2*m)) - ((resolution * degree_R * degree_R * normR)+ (resolution * red_node_blue_degree * blue_node_red_degree * normInter))
            

            modularityB = (fair_L_cB / m)+ (inter_L/(2*m)) - ((resolution * degree_B * degree_B * normB)+ (resolution * blue_node_red_degree * red_node_blue_degree * normInter))
            


            
            modularityCommunity = (L_c / m) - (resolution * out_degree_sum * in_degree_sum * norm)
            if modularityCommunity !=0:
                fairModPerc = (modularityR-modularityB)/abs(modularityCommunity)
            else:
                fairModPerc = 0
            return (modularityR-modularityB),fairModPerc,modularityR,modularityB

        else:
            return 0
    communitiesNum = 0
    for c in communities:
        if len(c)>0:
            communitiesNum+=1

    communityModularityist = []
    
    fairModPercList = []
    modularityRedList = []
    modularityBlueList = []
    
    for community in communities:
        
        communityContr = community_contribution(community)
        communityModularityist.append(communityContr[0])
        fairModPercList.append(communityContr[1])
        modularityRedList.append(communityContr[2])
        modularityBlueList.append(communityContr[3])
        
        
        
    return sum(communityModularityist),communityModularityist,fairModPercList,modularityRedList,modularityBlueList


def LModularityFairnessMetric(G, communities,G_attribute, weight="weight", resolution=1):
    """Populate L-attributes and evaluate L-modularity fairness for a partition.

    Initializes per-node counts for red/blue/inter incidences and per-edge
    indicators for red-only, blue-only, and inter-group connections using the
    provided binary node attribute mapping. It then calls
    ``compute_LmodularityFairness`` to compute fairness-aware signals.

    Args:
        G: NetworkX Graph to annotate and evaluate.
        communities: Partition of nodes as an iterable of sets/lists.
        G_attribute: Dict mapping node -> {0,1} group label.
        weight: Edge attribute used as base weight (default: "weight").
        resolution: Resolution parameter for the null model.

    Returns:
        (sum_diff, per_comm_diff_list, per_comm_norm_diff_list,
         per_comm_red_mod_list, per_comm_blue_mod_list)
    """
    
    for u in G.nodes():
        G.nodes[u]['red_weight'] = 0
        G.nodes[u]['blue_weight'] = 0
        G.nodes[u]['red_node_blue_weight'] = 0
        G.nodes[u]['blue_node_red_weight'] = 0
        G.nodes[u]['inter_weight'] = 0
    for u,v in G.edges():
        G[u][v]['r_weight'] = 0
        G[u][v]['b_weight'] = 0  
        G[u][v]['inter_weight'] = 0
        
    timesIn = 0
    for u,v in G.edges():
        if G_attribute[u] == 0 and G_attribute[v] == 0: # red
            G[u][v]['r_weight'] = 1
            G[u][v]['b_weight'] = 0
            
            
            
        elif G_attribute[u] == 1 and G_attribute[v] == 1: # blue
            G[u][v]['b_weight'] = 1
            G[u][v]['r_weight'] = 0
            
        else:
            G[u][v]['b_weight'] = 0
            G[u][v]['r_weight'] = 0
        if G_attribute[u] != G_attribute[v]:
            timesIn +=1
            
            G[u][v]['inter_weight'] = 1
            G.nodes[u]['inter_weight'] +=1
            #G.nodes[v]['inter_weight'] +=1
            
            
        if G_attribute[u] == 0 and G_attribute[v] == 0: # red
            G.nodes[u]['red_weight'] +=1        
            G.nodes[v]['red_weight'] +=1
        if G_attribute[u] == 1 and G_attribute[v] == 1: # blue
            G.nodes[u]['blue_weight'] +=1
            G.nodes[v]['blue_weight'] +=1
        if G_attribute[u] == 0 and G_attribute[v] == 1:
            G.nodes[u]['red_node_blue_weight'] +=1
            G.nodes[v]['blue_node_red_weight'] +=1
        elif G_attribute[u] == 1 and G_attribute[v] == 0:
            G.nodes[u]['blue_node_red_weight'] +=1
            G.nodes[v]['red_node_blue_weight'] +=1

        
            
    fairModularity,fairModularityList,fairModularityPerc,modularityRedList,modularityBlueList = compute_LmodularityFairness(G, communities, weight="weight", resolution=1)
    

    
    return fairModularity,fairModularityList,fairModularityPerc,modularityRedList,modularityBlueList
    
    