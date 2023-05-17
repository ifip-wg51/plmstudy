class GraphBuilder:

    def __init__(self, keywords): 
        self.keywords = keywords
        self.edges = []

    def addOrWeightEdge(self, keyA, keyB):
        index = -1
        for i, edge in enumerate(self.edges):
            #check for both directions
            if (edge['A'] == keyA and edge['B'] == keyB) or (edge['A'] == keyB and edge['B'] == keyA):
                edge['weight'] = edge['weight']+1
                index = i
                break
        if index == -1:
            index = len(self.edges)
            self.edges.append({
                'A': keyA,
                'B': keyB,
                'weight': 1
            })
        return index

    def build(self, publications):
        # loop through all publications
        # add edge for all keywords
        for pub in publications:
            for i, pubKeyA in enumerate(pub['keywords']):
                # only compare forward in the array (i+1) to avoid A = B and B = A (edges have no direction)
                for j in range(i+1, len(pub['keywords'])):
                    pubKeyB = pub['keywords'][j]
                    if pubKeyA != pubKeyB:
                        self.addOrWeightEdge(pubKeyA, pubKeyB)
        return
    
    def write(self, keywordFile, edgeFile):
        open(keywordFile, 'w').close()
        file = open(keywordFile, 'a')
        for i, key in enumerate(self.keywords):
            file.write(str(i) + ';' + str(key['keyword']) + ';' + str(key['count']) + "\n")
        file.close
        open(edgeFile, 'w').close()
        file = open(edgeFile, 'a')
        for edge in self.edges:
            file.write(str(edge['A']) + ';' + str(edge['B'])+ ';' + str(edge['weight']) + "\n")
        file.close
