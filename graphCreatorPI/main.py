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

from icplmReader import ICPLMReader
from Normalizer import Normalizer
from GraphBuilder import GraphBuilder


logfile = 'out/missing-keywords.txt'
normTableFile = '../database/PLM/PLM_normalized.csv'
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



print("Start building graph data")

print("... read source data")
reader = ICPLMReader(dbFile, 2005, 2011, isbns)
publications = reader.read()

print("... normalize keywords")
normalizer = Normalizer(normTableFile, logfile)
normalizer.normalize(publications)

print("... write publications")
normalizer.writePublications(publicationsFile, publications)

print("... build edges")
graph = GraphBuilder(normalizer.keywords)
graph.build(publications)
print ("... write output files")
graph.write(graphKeywordsFile, graphEdgesFile)

print("All done")
