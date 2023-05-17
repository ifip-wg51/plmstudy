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

import icplmReader as reader
from Normalizer import Normalizer
from GraphBuilder import GraphBuilder

logfile = 'out/missing-keywords.txt'
normTableFile = '../database/PLM/PLM_normalized.csv'
publicationsFile = 'out/publications.csv'
graphKeywordsFile = 'out/graphKeywords.csv'
graphEdgesFile = 'out/graphEdges.csv'

open(logfile, 'w').close()

print("Start building graph data")
publications = reader.read()
normalizer = Normalizer(normTableFile, logfile)
normalizer.normalize(publications)
normalizer.writePublications(publicationsFile, publications)

graph = GraphBuilder(normalizer.keywords)
graph.build(publications)
graph.write(graphKeywordsFile, graphEdgesFile)

