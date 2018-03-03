import traceback
import os.path
import sys
import itertools
import networkx as nx
import matplotlib.pyplot as plt

from itertools import izip, islice
from networkx.algorithms.distance_measures import center
    
class dependencygraph:

    def __init__(self):

        R1 = ''
        R2 = ''
        R3 = ''
        R4 = ''

        if os.path.exists('DependencyGraph.png'):
            os.remove('DependencyGraph.png')
        if os.path.exists('FeatureModel.png'):
            os.remove('FeatureModel.png')

        if os.path.exists('Refined-R1-FeatureRelations.txt'):
            with open('Refined-R1-FeatureRelations.txt','r') as f:
                R1 = f.read()
        if os.path.exists('Refined-R2-FeatureRelations.txt'):
            with open('Refined-R2-FeatureRelations.txt','r') as f:
                R2 = f.read()
        if os.path.exists('Refined-R3-FeatureRelations.txt'):
            with open('Refined-R3-FeatureRelations.txt','r') as f:
                R3 = f.read()
        if os.path.exists('Refined-R4-FeatureRelations.txt'):
            with open('Refined-R4-FeatureRelations.txt','r') as f:
                R4 = f.read()

        if os.path.exists('RootFeature.txt'):
            with open('RootFeature.txt','r') as f:
                rootFeature = f.read().lower()

        R1arr = R1.split('\n')
        R2arr = R2.split('\n')
        R3arr = R3.split('\n')
        R4arr = R4.split('\n')

        Relations = []
        NonRelations = []

        for arr in R2arr:
            r = filter(None, arr.split('->'))
            for current_item, next_item in izip(r, islice(r, 1, None)):
                NonRelations.append((current_item, next_item))
                NonRelations.append((next_item, current_item))
        print('DONE R2')

        for arr in R1arr:
            r = filter(None, arr.split('->'))
            if r and r[0] != '' and rootFeature in r[0]:
                r[0] = rootFeature
            for current_item, next_item in izip(r, islice(r, 1, None)):
                if (current_item, next_item) not in NonRelations:
                    if not [(x,y) for x, y in Relations if y == current_item] and current_item != rootFeature and next_item != rootFeature:                        
                        Relations.append((rootFeature, current_item))
                    if current_item != next_item and next_item != rootFeature:
                        Relations.append((current_item, next_item))
        print('DONE R1')

        for arr in R3arr:
            r = filter(None, arr.split('->'))
            if r and r[0] != '' and rootFeature in r[0]:
                r[0] = rootFeature
            for current_item, next_item in izip(r, islice(r, 1, None)):
                if (current_item, next_item) not in NonRelations:
                    if not [(x,y) for x, y in Relations if y == current_item] and current_item != rootFeature and next_item != rootFeature:
                        Relations.append((rootFeature, current_item))                    
                    if current_item != next_item and next_item != rootFeature:
                        Relations.append((current_item, next_item))
        print('DONE R3')

        for arr in R4arr:
            r = filter(None, arr.split('->'))
            if r and r[0] != '' and rootFeature in r[0]:
                r[0] = rootFeature
            for current_item, next_item in izip(r, islice(r, 1, None)):
                if (current_item, next_item) not in NonRelations:
                    if not [(x,y) for x, y in Relations if y == current_item] and current_item != rootFeature and next_item != rootFeature:
                        Relations.append((rootFeature, current_item))
                    if current_item != next_item and next_item != rootFeature:
                        Relations.append((current_item, next_item))
        print('DONE R4')

        G = nx.DiGraph()

        for (x,y) in Relations:
            if (y != rootFeature):
                G.add_edge(x, y)#, weight=1.0)

        # Convert graph to tree using BFS
        tree = nx.bfs_tree(G, rootFeature)

        if(nx.is_tree(tree)):
            # Get all central nodes
            H = nx.betweenness_centrality(tree,None,True)
            centralNodes = [key for key, val in H.items() if val > 0]

        Nodes = G.nodes()
        subGraphNodes=[]
        nonsensewords = [word.strip() for word in open("NonsenseWords.txt", "r")]

        for n1 in Nodes:
            for n2 in centralNodes:
                if (nx.has_path(G,n1,n2) and (n1 != n2) and (n1 not in nonsensewords) and (n2 not in nonsensewords)):
                    dist = nx.shortest_path(G,n1,n2)
                    subGraphNodes.append(n1)
                    subGraphNodes.append(n2)

        # Generating the sub graph
        H = G.subgraph(subGraphNodes)

        nx.draw(H, with_labels = True)
        plt.savefig("DependencyGraph.png") # save as png
        # plt.show() # display
        # save the .dot file
        nx.drawing.nx_pydot.write_dot(H, "grid.dot")

        print('DONE')


        

