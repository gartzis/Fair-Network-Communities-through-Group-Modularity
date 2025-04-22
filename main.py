
import sys
import os






sys.path.append('Algorithms')
from diversityFairness import diversityMetric
from modularityFairness import modularityFairnessMetric
from L_diversityFairness import LDiversityFairnessMetric
from L_modularityFairness import LModularityFairnessMetric


sys.path.append('Community Detection')

from redModularityLouvain import redFairness_louvain_communities
from blueModularityLouvain import blueFairness_louvain_communities
from LredModularityLouvain import LRedFairness_louvain_communities
from LblueModularityLouvain import LBlueFairness_louvain_communities
from diversityFairnessLouvain import diversityFairness_louvain_communities
from LdiversityLouvain import Ldiversity_louvain_communities


import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt



def computeMetrics(G, communities,G_attribute):
    modularity = nx.algorithms.community.modularity(G, communities, weight="weight")
    diversitymodularity,diversityModularityList = diversityMetric(G, communities,G_attribute, weight="weight", resolution=1)
    unfairness,unfairnessList,unfairnessModularityPerc,redModularityList,blueModularityList = modularityFairnessMetric(G, communities,G_attribute, weight="weight", resolution=1)
    lUnfairness,lUnfairnessList,lUnfairnessModularityPerc,lRedList,lBlueList = LModularityFairnessMetric(G, communities,G_attribute, weight="weight", resolution=1)
    lDiversity,lDiversityList = LDiversityFairnessMetric(G, communities,G_attribute, weight="weight", resolution=1)
    
    print('\nModularity:',modularity)
    print('---------------------')
    print('RedModularity:',sum(redModularityList),'\tBlueModularity:',sum(blueModularityList))
    print('L-Red Modularity',sum(lRedList),'\tL-Blue Modularity',sum(lBlueList))
    print('---------------------')
    print('Unfairness',unfairness,'\tDiversity:',diversitymodularity)
    print('L-Unfairness:',lUnfairness,'\tL-Diversity:',lDiversity)

def plotCommunities(G, node_attributes_dict, communities, file_name, plotName,method):
    # Assuming you have G, node_attributes_dict, and communities already computed from your code

    # List of different markers for communities
    community_markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'H', 'X']

    plt.figure().set_size_inches(22, 19)
    # Generate a layout for the graph (e.g., spring layout)
    pos = nx.spring_layout(G)

    # Draw the edges
    nx.draw_networkx_edges(G, pos, alpha=0.5)

    # Draw nodes for each community with attribute-specific colors and different markers
    for community_id, community_nodes in enumerate(communities):
        community_marker = community_markers[community_id % len(community_markers)]  # Cycle through markers if more than available
        
        # Assign colors for each node based on its attribute (red for 0, blue for 1)
        node_colors = []
        for node in community_nodes:
            if node_attributes_dict[node] == 0:
                node_colors.append('red')  # Red for attribute == 0
            else:
                node_colors.append('blue')  # Blue for attribute == 1
        
        # Draw the nodes for the current community with attribute-based colors
        nx.draw_networkx_nodes(G, pos, nodelist=community_nodes, 
                               node_color=node_colors,  # Attribute-based color
                               label=f'Community {community_id}',
                               node_size=300, alpha=1, linewidths=1, node_shape=community_marker)  # Increase node size, linewidths, and use different markers

    # Draw labels (optional)
    nx.draw_networkx_labels(G, pos, font_size=10)

    # Add a legend for the communities
    legend_patches = []
    for community_id in range(len(communities)):
        community_marker = community_markers[community_id % len(community_markers)]
        patch = plt.Line2D([0], [0], marker=community_marker, color='w', label=f'Community {community_id}',
                           markerfacecolor='gray', markersize=10)
        legend_patches.append(patch)

    # Add red/blue legend for node attributes
    red_patch = plt.Line2D([0], [0], marker='o', color='w', label='Attribute 0 (red)',
                           markerfacecolor='red', markersize=10)
    blue_patch = plt.Line2D([0], [0], marker='o', color='w', label='Attribute 1 (blue)',
                            markerfacecolor='blue', markersize=10)

    # Display legend combining communities and attributes
    plt.legend(handles=legend_patches + [red_patch, blue_patch], loc='best')
    
    plt.savefig('Synth Results\{}\{}\{}.png'.format(method,file_name, plotName))
    plt.close()
    #plt.show()


data_path = 'Data\Symmetric'
data_path = 'Data\Assymetric'

file_paths = [os.path.join(data_path, file.split('.')[0]) for file in os.listdir(data_path)]
file_paths = list(set(file_paths))



datasets = file_paths

# Initialize an empty DataFrame with the specified columns
results_df = pd.DataFrame(columns=[
    'dataset', 'method', 'communities', 'modularity_B', 'redModularityList', 
    'blueModularityList', 'fmod_B', 'diversity_B', 'fairnessDiversity_B', 
    'fairnessModularity_B', 'balance_B', 'max_redBalance_B','min_redBalance_B', 'max_blueBalance_B','min_blueBalance_B'
])

# Function to append results to the DataFrame
def append_results(dataset, method, line):
    global results_df
    results_df = results_df.append({
        'dataset': dataset,
        'method': method,
        'communities': len(line[0]),
        'modularity_B': line[1],
        'redModularityList': line[2],
        'blueModularityList': line[3],
        'fmod_B': line[4],
        'diversity_B': line[5],
        'fairnessDiversity_B': line[6],
        'fairnessModularity_B': line[7],
        'balance_B': line[8],
        'max_redBalance_B': line[9],
        'min_redBalance_B': line[10],
        'max_blueBalance_B': line[11],
        'min_blueBalance_B': line[12]
        
    }, ignore_index=True)



if not os.path.exists('Synth Results'):
    os.makedirs('Synth Results')


for file_path in datasets:
    datasetName= file_path.split('\\')[-1]
    print(datasetName)
    
    datasetRead = file_path+'\\'+datasetName

    
    graph = nx.read_edgelist(datasetRead+'.edgelist', nodetype=int, create_using=nx.Graph())
    graph_attributes = pd.read_csv(datasetRead+'.csv', index_col=2, dtype={'attribute': int}).to_dict()['attribute']
    
    nx.set_node_attributes(graph, graph_attributes, 'attribute')
    
    if not os.path.exists('Synth Results\\RedMod Communities'):
        os.makedirs('Synth Results\\RedMod Communities')
        
    if not os.path.exists('Synth Results\\RedMod Communities\\'+datasetName):
        os.makedirs('Synth Results\\RedMod Communities\\'+datasetName)
        
    print('---Red Modularity---')
        
    red_communities = redFairness_louvain_communities(graph, weight="weight", resolution=1,node_attributes=graph_attributes)
    
    print('Number of communities:',len(red_communities))
    # Compute metrics for the red communities
    computeMetrics(graph, red_communities, graph_attributes)
    
    plotName = datasetName+'_Red_Louvain'
    plotCommunities(graph, graph_attributes, red_communities, datasetName, plotName,'RedMod Communities')
    
    # Create a DataFrame from the red_communities
    
    community_df = pd.DataFrame([(node, community) for community, nodes in enumerate(red_communities) for node in nodes], columns=['node', 'community'])
    
    # Write the DataFrame to a CSV file
    
    community_df.to_csv(os.path.join('Synth Results\\RedMod Communities\\'+datasetName, datasetName + '_communities.csv'), index=False)
    
    print('\n---Blue Modularity---')
    
    if not os.path.exists('Synth Results\\BlueMod Communities'):
        os.makedirs('Synth Results\\BlueMod Communities')
        
    if not os.path.exists('Synth Results\\BlueMod Communities\\'+datasetName):
        os.makedirs('Synth Results\\BlueMod Communities\\'+datasetName)
        
    blue_communities = blueFairness_louvain_communities(graph, weight="weight", resolution=1,node_attributes=graph_attributes)
    
    print('Number of communities:',len(blue_communities))
    # Compute metrics for the blue communities
    computeMetrics(graph, blue_communities, graph_attributes)
    
    plotName = datasetName+'_Blue_Louvain'
    plotCommunities(graph, graph_attributes, blue_communities, datasetName, plotName,'BlueMod Communities')
    
    # Create a DataFrame from the blue_communities
    
    community_df = pd.DataFrame([(node, community) for community, nodes in enumerate(blue_communities) for node in nodes], columns=['node', 'community'])
    
    # Write the DataFrame to a CSV file
    
    community_df.to_csv(os.path.join('Synth Results\\BlueMod Communities\\'+datasetName, datasetName + '_communities.csv'), index=False)
    
    
    print('\n---L-Red Modularity---')
    if not os.path.exists('Synth Results\\L-RedMod Communities'):
        os.makedirs('Synth Results\\L-RedMod Communities')
        
    if not os.path.exists('Synth Results\\L-RedMod Communities\\'+datasetName):
        os.makedirs('Synth Results\\L-RedMod Communities\\'+datasetName)
        
    red_communities = LRedFairness_louvain_communities(graph, weight="weight", resolution=1,node_attributes=graph_attributes)
    
    print('Number of communities:',len(red_communities))
    # Compute metrics for the red communities
    computeMetrics(graph, red_communities, graph_attributes)
    
    plotName = datasetName+'_L-Red_Louvain'
    plotCommunities(graph, graph_attributes, red_communities, datasetName, plotName,'L-RedMod Communities')
    
    # Create a DataFrame from the red_communities
    
    community_df = pd.DataFrame([(node, community) for community, nodes in enumerate(red_communities) for node in nodes], columns=['node', 'community'])
    
    # Write the DataFrame to a CSV file
    
    community_df.to_csv(os.path.join('Synth Results\\L-RedMod Communities\\'+datasetName, datasetName + '_communities.csv'), index=False)
    
    
    print('\n---L-Blue Modularity---')
    if not os.path.exists('Synth Results\\L-BlueMod Communities'):
        os.makedirs('Synth Results\\L-BlueMod Communities')
        
    if not os.path.exists('Synth Results\\L-BlueMod Communities\\'+datasetName):
        os.makedirs('Synth Results\\L-BlueMod Communities\\'+datasetName)
        
    blue_communities = LBlueFairness_louvain_communities(graph, weight="weight", resolution=1,node_attributes=graph_attributes)
    
    print('Number of communities:',len(blue_communities))
    # Compute metrics for the blue communities
    computeMetrics(graph, blue_communities, graph_attributes)
    
    plotName = datasetName+'_L-Blue_Louvain'
    plotCommunities(graph, graph_attributes, blue_communities, datasetName, plotName,'L-BlueMod Communities')
    
    # Create a DataFrame from the blue_communities
    
    community_df = pd.DataFrame([(node, community) for community, nodes in enumerate(blue_communities) for node in nodes], columns=['node', 'community'])
    
    # Write the DataFrame to a CSV file
    
    community_df.to_csv(os.path.join('Synth Results\\L-BlueMod Communities\\'+datasetName, datasetName + '_communities.csv'), index=False)
    
    
    print('\n---Diversity Modularity---')
    if not os.path.exists('Synth Results\\DiversityMod Communities'):
        os.makedirs('Synth Results\\DiversityMod Communities')
        
    if not os.path.exists('Synth Results\\DiversityMod Communities\\'+datasetName):
        os.makedirs('Synth Results\\DiversityMod Communities\\'+datasetName)
        
    diversity_communities = diversityFairness_louvain_communities(graph, weight="weight", resolution=1,node_attributes=graph_attributes)
    
    print('Number of communities:',len(diversity_communities))
    # Compute metrics for the diversity communities
    computeMetrics(graph, diversity_communities, graph_attributes)
    
    plotName = datasetName+'_Diversity_Louvain'
    plotCommunities(graph, graph_attributes, diversity_communities, datasetName, plotName,'DiversityMod Communities')
    
    # Create a DataFrame from the diversity_communities
    
    community_df = pd.DataFrame([(node, community) for community, nodes in enumerate(diversity_communities) for node in nodes], columns=['node', 'community'])
    
    # Write the DataFrame to a CSV file
    
    community_df.to_csv(os.path.join('Synth Results\\DiversityMod Communities\\'+datasetName, datasetName + '_communities.csv'), index=False)
    
    
    
    
    print('\n---L-Diversity Modularity---')
    if not os.path.exists('Synth Results\\L-DiversityMod Communities'):
        os.makedirs('Synth Results\\L-DiversityMod Communities')
        
    if not os.path.exists('Synth Results\\L-DiversityMod Communities\\'+datasetName):
        os.makedirs('Synth Results\\L-DiversityMod Communities\\'+datasetName)
        
    diversity_communities = Ldiversity_louvain_communities(graph, weight="weight", resolution=1,node_attributes=graph_attributes)
    
    print('Number of communities:',len(diversity_communities))
    # Compute metrics for the diversity communities
    computeMetrics(graph, diversity_communities, graph_attributes)
    
    plotName = datasetName+'_L-Diversity_Louvain'
    plotCommunities(graph, graph_attributes, diversity_communities, datasetName, plotName,'L-DiversityMod Communities')
    
    # Create a DataFrame from the diversity_communities
    
    community_df = pd.DataFrame([(node, community) for community, nodes in enumerate(diversity_communities) for node in nodes], columns=['node', 'community'])
    
    # Write the DataFrame to a CSV file
    
    community_df.to_csv(os.path.join('Synth Results\\L-DiversityMod Communities\\'+datasetName, datasetName + '_communities.csv'), index=False)
    
