import networkx as nx
import pandas as pd



def compute_modularityFairness(G, communities, weight="weight", resolution=1):
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
    
    