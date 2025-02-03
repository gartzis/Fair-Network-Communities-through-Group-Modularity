# Fair-Network-Communities-through-Group-Modularity


# Introduction

Networks are essential for representing and analyzing interconnected systems across different domains, such as in social, collaboration, and citation settings. Nodes in networks often form communities, i.e., subsets of nodes that are more tightly connected with each other than with nodes outside the community. Connections in networks play a pivotal role in shaping opinions and influencing decision-making processes. In this paper, we study the *fairness* of connections within network communities.

To model fairness of connections, we use modularity. Modularity is a measure of the quality of community structures in networks
that quantifies the strength of the division of a network into communities by comparing the density of edges within communities to the expected density in a random graph. We introduce a variation of modularity, termed group modularity, that considers the density of edges of nodes belonging to a specific group.

To locate fair community structures in a networks, we propose a fairness-aware community detection algorithm. The algorithm builds on the Louvain algorithm, an agglomerative hierarchical method, where sets of nodes are successively merged to form larger communities such that modularity increases. In the proposed fairness-aware algorithms, the criterion for merging communities takes into account the fairness and diversity of the communities.

