
def computeDiversityFairness(G, communities, weight="weight", resolution=1):
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
        
        norm = 1 /(2*(m**2))



        degrees_red = dict(G.nodes(data="red_weight"))
        degrees_blue = dict(G.nodes(data="blue_weight"))

    def community_contribution(community):
        if len(community)>0:
            comm = set(community)

            degree_R = sum(degrees_red[u] for u in comm)
            degree_B = sum(degrees_blue[u] for u in comm)

 
            inter_L =sum(wt for u, v, wt in G.edges(comm, data="inter_weight", default=1) if v in comm)
            
            
            
           
            modularityCommunityInter = (inter_L / (2*m)) - ((resolution * degree_R * degree_B * norm))
            
            
            return modularityCommunityInter

        else:
            return 0
    communitiesNum = 0
    for c in communities:
        if len(c)>0:
            communitiesNum+=1

    
    communityInterModularityList = []
    
    
    for community in communities:
        
        communityInterModularityList.append(community_contribution(community))

        
        
        
    return sum(communityInterModularityList),communityInterModularityList


def LDiversityFairnessMetric(G, communities,G_attribute, weight="weight", resolution=1):
    
    

    
    for u in G.nodes():
        G.nodes[u]['red_weight'] = 0
        G.nodes[u]['blue_weight'] = 0
        G.nodes[u]['inter_weight'] = 0

    for u,v in G.edges():
        if G_attribute[u] == 0 and G_attribute[v] == 0: # red
            G[u][v]['r_weight'] = 1
            G[u][v]['b_weight'] = 0
            G[u][v]['inter_weight'] = 0
            
        elif G_attribute[u] == 1 and G_attribute[v] == 1: # blue
            G[u][v]['b_weight'] = 1
            G[u][v]['r_weight'] = 0
            G[u][v]['inter_weight'] = 0
        else:
            G[u][v]['b_weight'] = 0
            G[u][v]['r_weight'] = 0
            G[u][v]['inter_weight'] = 1

        if G_attribute[u] == 0: # red
            G.nodes[u]['red_weight'] +=1
        if G_attribute[u] == 1:
            G.nodes[u]['blue_weight'] +=1
        if G_attribute[v] == 0:
            G.nodes[v]['red_weight'] +=1
        if G_attribute[v] == 1:
            G.nodes[v]['blue_weight'] +=1
        if G_attribute[u] != G_attribute[v]:
            G.nodes[u]['inter_weight'] +=1
            G.nodes[v]['inter_weight'] +=1

            
            
        
            
    diversityModularity,divercityModularityList = computeDiversityFairness(G, communities, weight="weight", resolution=1)
    
    
    return diversityModularity,divercityModularityList