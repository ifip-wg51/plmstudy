# GraphCerator
# This code takes a list of publications and their keywords and creates a data 
# file with a co-occurrence graph based on keywords, that can be used by Gephi to visualize
#
# Steps for the procedure
# 1. Read the input data in json format { titel: "", "keyword": [] } with a datareader
# 2. Normalize the keywords (based on normalized.csv and abbreviation.csv)
# 3. Build edges for the graph
# 4. Write nodes and edges to files

# Global Settings
import numpy as np
import matplotlib.pyplot as plt
from icplmReader import ICPLMReader
from Normalizer import Normalizer
from GraphBuilder_Raw import GraphBuilderRAW
from GraphBuilder_WordTree import GraphBuilderWordTree
from GraphBuilder_KWA import GraphBuilderKWA
import json

logfile = 'out/missing-keywords.txt'
normTableFile = '../database/PLM/PLM_normalized-02.csv'
publicationsFile = 'out/publications.csv'
graphKeywordsFile = 'out/graphKeywords.csv'
graphEdgesFile = 'out/graphEdges.csv'
dbFile = '../database/PLM/PLM_analysis.sqlite'
isbns = [
    "978-3-319-54660-5", #2016
    "978-3-319-72905-3", #2017
    "978-3-030-01614-2", #2018
    "978-3-030-42250-9", #2019
    "978-3-030-62807-9", #2020
    "978-3-030-94335-6", #2021 Part 1
    "978-3-030-94399-8", #2021 Part 1
    "978-3-031-25182-5", #2022
]
# Process Settings
buildGraph = True
thAnalysis = False

def importAndNormalize():
    print("... rebuilding raw graph data")
    print("... read source data")
    reader = ICPLMReader(dbFile, 2005, 2011, isbns)
    publications = reader.read()
    # print(publications)
    print("... normalize keywords")
    normalizer = Normalizer(normTableFile, logfile)
    normalizer.normalize(publications)
    print("... write publications")
    normalizer.writePublications(publicationsFile, publications)
    print("... save raw data")
    saveJSON('out/graph',normalizer.keywords, publications)
    return

def analyze():
    thcNodeCount = []
    thcIgnored = []
    thc = []
    thc.append(-1)
    nodeReuction = 5
    c = 0
    print("... ref plot")
    graphRaw.plotKeywords('out/refplot.png', 2500, 350, False)
    graphRaw.plotKeywords('out/refplot-scaled.png', 200, 50, False)
    for key in graphRaw.keywords:
        if graphRaw.keywords[key]['count'] > nodeReuction:
            c += 1
    ign = len(graphRaw.keywords) - c
    for i in range(0, 10, 1):
        print("    Threshold: " + str(i))
        graphWT.condenseByCommonWords(i, 10)
        graphWT.writeCondensedKeywordsJSON('out/condensedKeywords')
        # remove dominating nodes
        graphWT.removeNodes(['product lifecycle management', 'product ...'])
        res = graphWT.plotNodes('out/threshold-' + str(i) + '.png', False)
        thcNodeCount.append(res['nodes'])
        thcIgnored.append(res['ignored'])
        thc.append(i)
    plt.plot(0, c, label = "keywords > " + str(nodeReuction) )
    plt.plot(0, ign, label = "orig. ignored")
    plt.plot(thc, thcNodeCount, label = "nodes")
    plt.plot(thc, thcIgnored, label = "ignored")
    plt.xlabel('Threshold')
    plt.legend()
    plt.savefig('out/threshold.png')
    plt.close()

################################################################
#   Methods for output

def saveJSON(filename, keywords, publications):
    rootObject = {
        'keywords' : keywords,
        'publication' : publications,
    }  
    file = open(filename + '.json', 'w')
    file.write(json.dumps(rootObject, indent = 4))
    file.close()
    return

def loadJSON(filename):
    file = open(filename + '.json', 'r')
    rootObject = json.loads(file.read())
    file.close()
    return rootObject

################################################################
#   Main Program

print("-------------------------")
print("Start building graph data")

if buildGraph:
   importAndNormalize()
   root = loadJSON('out/graph')
else:
    print("... load raw data")
    root = loadJSON('out/graph')

print("... raw build graph")
graphRaw = GraphBuilderRAW(root['keywords'], root['publication'])
graphRaw.build()

graphWT = GraphBuilderWordTree(root['keywords'], root['publication'])

print("... build condense keywords graph")
if thAnalysis:
    analyze()

graphWT.build(4, 10)
graphWT.writeJSON('out/condensedKeywords')
graphWT.writeGephi('out/condensedKeywords')
graphWT.writeIgnoredKeywords('out/ignodedKeywords.csv')

graphKWA = GraphBuilderKWA(root['keywords'], root['publication'])
graphKWA.build()
graphKWA.write('out/kwaTable')

print("All done")
print("-------------------------")