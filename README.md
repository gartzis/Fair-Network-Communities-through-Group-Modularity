# Fair-Network-Communities-through-Group-Modularity

An implementation of the The Web Conference 2025 paper "Fair Network Communities through Group Modularity"

This repository implements community detection algorithms that incorporate fairness and diversity based on the Louvain algorithm. These algorithms aim to identify communities in graphs while considering sensitive attributes (e.g., demographic groups). The focus is on both group modularity and fairness, ensuring that the discovered communities respect edge based metrics such as the diversity, unfairness and group-modularity of different groups.

### Directory Structure
- **Algorithms/**: Contains Python implementations for the community metrics.

    - `modularityFairness.py`: Implements Group-Modularity and the Unfairness metric.

    - `diversityFairness.py`: Implements Diversity fairness metric.

    - `L_modularityFairness.py`: Implements L-Group-Modularity metric and the L-Unfairness metric.

    - `LdiversityFairness.py`: Implements the L-Diversity fairness metric.




- **Community Detection/**: Contains Python implementations for the community detection methods.

  - `LredModularityLouvain.py`: L-Goup-Modularity-based (_Red Group_) community detection implementation.

  - `LblueModularityLouvain.py`: L-Goup-Modularity-based (_Blue Group_) community detection implementation.

  - `LdiversityLouvain.py`: L-Diversity-based community detection implementation.

  - `redModularityLouvain.py`: Goup-Modularity-based (_Red Group_) community detection implementation.

  - `blueModularityLouvain.py`: Goup-Modularity-based (_Blue Group_) community detection implementation.

  - `diversityFairnessLouvain.py`: Diversity-based community detection implementation.


### Fairness-Aware Louvain Algorithm

The core algorithm is an extension of the Louvain algorithm, which is a widely-used method for detecting communities based on modularity. The **fairness-aware Louvain** algorithm integrates additional fairness constraints to ensure that communities formed from graphs respect group-based fairness.

**Fairness Constraints**:

   - **Group-Increase**: Increase modularity for the underrepresented group to reduce imbalance.
   - **Fairness-Gain**: Decrease unfairness (absolute value) between groups.
   - **Diversity-Increase**: Increase diversity.

The fairness-aware Louvain algorithm operates iteratively, merging communities that both increase modularity and respect fairness criteria. These implementations focus on different measures, such as **Red/Blue Modularity** and **Diversity**, **L-Diversity**.

### Fairness Metrics

   1. **Unfairness**: Measures whether one group is more densely connected than the other in community.
   2. **L-Unfairness**: Extends unfairness to labeled groups, where we know the color of both edge endpoints.
   3. **Diversity**: Focuses on ensuring diversity within communities by increasing cross-group edges.
   4. **L-Diversity**: Focuses on ensuring L-diversity within communities by increasing cross-group edges.




### How to Use

1. **Installation Requirements**:
   The project requires Python and the following dependencies:
   - `networkx`: For graph-related tasks.
   - `numpy`: For mathematical operations.
   - `scipy`: For sparse matrix computations.
   - `matplotlib`: For visualization.
   - `pandas`: For data handling.

2. **Usage Example**:
   To run a fairness-aware community detection algorithm, import the relevant method from the respective file and execute it on a graph object (`networkx.Graph`).

   Example:
   ```python
   from LredModularityLouvain import redFairness_louvain_communities
   import networkx as nx
   import pandas as pd

   # Load your graph
   G = nx.read_edgelist('your_graph.edgelist')

   # Assign attributes to the nodes (e.g., 'red' and 'blue' groups)
   node_attributes = pd.read_csv('your_graph.csv', index_col=2, dtype={'attribute': int}).to_dict()['attribute']

   # Run fairness-aware Louvain algorithm
   communities = redFairness_louvain_communities(G, node_attributes)

3. **Metrics Calculation**:
    Once communities are identified, the unfairness and modularity of the communities can be computed by importing ithe relevant metric

    Example:
    To compute the Unfairness and -Group Modularity metrics
    ```python
    from modularityFairness import modularityFairnessMetric
    import networkx as nx
    import pandas as pd

   # Load your graph
   G = nx.read_edgelist('your_graph.edgelist')

   # Assign attributes to the nodes (e.g., 'red' and 'blue' groups)
   node_attributes = pd.read_csv('your_graph.csv', index_col=2, dtype={'attribute': int}).to_dict()['attribute']

   # Run fairness metrics
   unfairness, unfairnessList, unfairnessModularityPerc, redMod, blueMod = modularityFairnessMetric(G, communities, node_attributes)

4. **Plotting Communities**:
    The function plotCommunities can be used to visualize the graph with communities highlighted, where nodes are colored based on their attributes.

    ```python
    plotCommunities(G, node_attributes, communities, 'example_graph', 'example_plot', 'method_used')



### Evaluation

The algorithms are evaluated using both synthetic and real-world datasets. Synthetic datasets are created using the **Stochastic Block Model** with different parameters controlling group sizes and homophily. Real-world datasets include social network data such as **Pokec**, **Deezer**, **Facebook**, and **Twitch**.

### Experimental Results

The results show that the fairness-aware algorithms significantly reduce unfairness (i.e., group modularity imbalances) and improve diversity in the communities. However, a trade-off exists between fairness and the number of communities, as increasing fairness may lead to smaller, more fragmented communities.

### Real-World Datasets:

   - **Pokec**: A social network with gender and age attributes.
   - **Deezer**: Music streaming service social network with gender-based groups.
   - **Facebook**: Social network with gender and education attributes.
   - **Twitch**: Online gaming platform with user relationships and gender-based groups.




[![DOI](https://zenodo.org/badge/926196014.svg)](https://doi.org/10.5281/zenodo.14794611)
