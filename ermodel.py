# CPSC 672 Project

# This script builds 1000 directed ER models given n and p and prints out the average clusering coefficient, 
# standard deviation of clustering coeff, number of strongly and weakly connected components. 
# It also outputs the degree distribution in log scale.

# Import statements
import networkx as nx
import statistics
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# Global arrays to calculate average
clusters = []
degrees = []
scomp = []
wcomp = []
dd = []


# Build ER model 1000 times and calculate clustering and degree for each network
# and add it to the respective arrays
for x in range(1000):
    rg = nx.erdos_renyi_graph(200, (3.39/199), directed=True)
    clusters.append(nx.average_clustering(rg))
    d = [rg.degree(node) for node in rg]
    dd = dd + d
    degrees.append(len(rg.edges())/len(rg))

    wcomp.append(nx.number_weakly_connected_components(rg))
    scomp.append(nx.number_strongly_connected_components(rg))


# Print Average Clustering Coefficient and the standard deviation
print('Avg Clustering coeffecient: ', sum(clusters)/len(clusters))
print('Standard dev. clustering: ', statistics.pstdev(clusters))

# Print average strongly and weakly connected components
print('Avg strong comp: ', sum(scomp)/len(scomp))
print('Avg weak comp: ', sum(wcomp)/len(wcomp))

# To make sure we have the same average degree as out real network
print('Avg Degree: ', sum(degrees)/len(degrees))

# Logscale does not accept 0 degree nodes
degr = [i for i in dd if i > 0]

bin_edges = np.logspace(np.log10(min(degr)), np.log10(max(degr)), num=10)

# histogram the data into these bins
density, _ = np.histogram(degr, bins=bin_edges, density=True)


fig = plt.figure(figsize=(6,4))

# "x" should be midpoint (IN LOG SPACE) of each bin
log_be = np.log10(bin_edges)
x = 10**((log_be[1:] + log_be[:-1])/2)

plt.loglog(x, density, marker='o', linestyle='none')

# Add axis labels
plt.xlabel(r"Degree $k$", fontsize=16)
plt.ylabel(r"$P(k)$", fontsize=16)

# remove right and top boundaries because they're ugly
ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')

# Show the plot
plt.show()


