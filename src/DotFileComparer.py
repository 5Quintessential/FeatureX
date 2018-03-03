import networkx as nx
import traceback

from nltk.corpus import wordnet as wn

## ********************* READ ME ***************************
## This program will compare the 3 dot files and extract
## meaningful relationship types like mandatory features,
## optional features, OR features and mutually exclusive 
## features. We do not have a mechanism to automatically
## extract cross tree constraints.
## The results from this execution can then be checked by
## a product line domain expert who can then make adjustments
## to the tree structure and add required cross tree constraints
## to design a complete feature model (FM) using any designer
## tools like Feature-IDE.
## *********************************************************

class dotfilecomparer:
    def __init__(self):
        try:
            mandatory = []
            orfeatures = []
            optional = []
            alternative = []

            G = nx.drawing.nx_pydot.read_dot('FM1.dot')
            H = nx.drawing.nx_pydot.read_dot('FM2.dot')
            I = nx.drawing.nx_pydot.read_dot('FM3.dot')
        
            h_edges = H.edges()
            g_edges = G.edges()
            i_edges = I.edges()

            h_nodes = H.nodes()
            g_nodes = G.nodes()
            i_nodes = I.nodes()

            similarnodes = []

            for node in g_nodes:
                words = node.split()
                for _node in h_nodes:
                    wrds = _node.split()
                    for __node in i_nodes:
                        wds = __node.split()
                        # if the whole phrase or its synonyms match then add to similarnodes
                        for w in words:
                            for synset in wn.synsets(w):
                                 for synonym in synset.lemmas(): 
                                     if str(synonym.name()).lower() in wrds and str(synonym.name()).lower() in wds:
                                         similarnodes.append((node,_node,__node))

            similarnodes = list(set(similarnodes))

            for (n1,n2,n3) in similarnodes:
                lst_gn = G.to_undirected().edges(n1)
                lst_hn = H.to_undirected().edges(n2)
                lst_in = I.to_undirected().edges(n3)                
                for (x,y) in lst_gn:
                    for (w,z) in lst_hn:
                        for (m,n) in lst_in:
                            if (x == w or self.aresimilar(x, w)) and (w == m or self.aresimilar(w, m)):
                                if (y == z or self.aresimilar(y, z)) and (z == n or self.aresimilar(z, n)):
                                    mandatory.append((x,y))
                                    mandatory.append((w,z))
                                    mandatory.append((m,n))
                                else:
                                    alternative.append((x,y))
                                    alternative.append((w,z))
                                    alternative.append((m,n))
                            else:
                                orfeatures.append((x,y))

            for (n1,n2) in H.edges():
                if (n1,n2) not in mandatory and (n1,n2) not in alternative and (n1,n2) not in orfeatures:
                    optional.append((n1,n2))

            for (n1,n2) in I.edges():
                if (n1,n2) not in mandatory and (n1,n2) not in alternative and (n1,n2) not in orfeatures:
                    optional.append((n1,n2))

            with open('Mandatory.txt', "a") as f:
                for (x,y) in list(set(list(mandatory))):
                    f.write(x + '->' + y)
                    f.write('\n')

            with open('Optional.txt', "a") as f:
                for (x,y) in list(set(list(optional))):
                    f.write(x + '->' + y)
                    f.write('\n')

            with open('Alternative.txt', "a") as f:
                for (x,y) in list(set(list(alternative))):
                    f.write(x + '->' + y)
                    f.write('\n')

            with open('OrFeatures.txt', "a") as f:
                for (x,y) in list(set(list(orfeatures))):
                    f.write(x + '->' + y)
                    f.write('\n')
        except Exception: 
            traceback.print_exc()
            pass

    def aresimilar(self, word1, word2):
        w1arr = word1.split()
        w2arr = word2.split()
        for w1 in w1arr:
            for ss in wn.synsets(w1):
                for syn in ss.lemmas(): 
                    if str(syn.name()).lower() in w2arr:
                        return True
        return False
