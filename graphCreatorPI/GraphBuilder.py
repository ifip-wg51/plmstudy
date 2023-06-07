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
        #Node Table
        open(keywordFile, 'w').close()
        file = open(keywordFile, 'a')
        file.write("Id;Label;Timestamp;Count;Time_count\n")
        for i, key in enumerate(self.keywords):
            timeInterval = "<["
            countInterval = "<"
            for y in key['years']:
                #timeInterval += "[" + str(y['year']) + "," + str(y['year']+1) + "]"
                timeInterval += str(y['year']) + ","
                countInterval += "[" + str(y['year']) + "," + str(y['count']) + "]"
            timeInterval += "]>"
            countInterval += ">"
            file.write(str(i) + ';' + str(key['keyword']) + ';' + timeInterval + ';' + str(key['count']) + ';' + countInterval + "\n")
        file.close

        #Edge Table
        open(edgeFile, 'w').close()
        file = open(edgeFile, 'a')
        file.write("Source;Target;Type;Weight\n")
        for edge in self.edges:
            file.write(str(edge['A']) + ';' + str(edge['B']) + ';Undirected;' + str(edge['weight']) + "\n")
        file.close
