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

import  icplmReader as reader

print("Start building graph data")
reader.read()

