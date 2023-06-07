class GraphBuilder:

    def __init__(self, keywords): 
        self.keywords = keywords
        self.edges = []
        self.clusters = []

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
        return
    
    def removePrepositionsAndArticles(self, keyword):
        return
    
    def findCluster(self, sequence):
        cluster = None
        for cl in self.clusters:
            if cl['cluster'] == sequence:
                cluster = cl
                break
        return cluster
    
    def aggregateByCommonWords(self):
        # Idea: if keywords share the same sequence of words they are 
        # similar an can be aggregated into a cluster
        # (e.g. start with information or contain agile)
        # rules: 
        #  1. Prepositions and articles are ignored
        #  2. if several words are possible, the first word has priority
        #  3. if a combination of words (e.g. information technology) this 
        #     will create a new cluster. The cluster with the most words has priority 
        #     (information technology system will win over information technology)
        #     Optional idea: These clusters could be "sub-clusters"
        #  4. If the count of a full keyword is higher than it would be with cluster of single words 
        #     the keyword has priority (e.g models for manufacturing has count of 10, model without 
        #     "models for manufacturing" has a count of 2 -> results in two clusters: 
        #     "models for manufacturing":10, and "models":2) 
        #  5. Clusters of size 1 will be ignored
        #  6. relations of aggregated keywords are merged
        #
        # Algorithm:
        # 1. Remove prepositions and articles for all keywords
        # 2. Take keyword i
        # 3. Take the full sequence of keyword
        # 4. Check if cluster already exists
        # 5. Check if any of the remaining keywords (i+1) contains the same sequence: 
        #    here it gets tricky: contains or starts with? What happens with the other keyword
        #    (it needs to be remove from the list to be processed, however it it start with 
        #    another keyword, we would prefer keywords by it's historic order which does not make sense)
        #    For now: compare = starts with
        # 6. If yes, create new cluster
        # 7. Else remove last word of sequence, repeat from 4.
        # 8. If no cluster was found, add keyword to list of single keywords
        # 9. Repeat from 2. until all keywords are processed

        self.clusters = []
        singleKeywords = []
        # 1. Remove prepositions and articles for all keywords
        for i, key in enumerate(self.keywords):
            key['keyword'] = self.removePrepositionsAndArticles(key['keyword'])
            if len(key['keyword']) == 1:
                singleKeywords.append(key)
            else:
                self.keywords[i] = key
        # 2. Take keyword i
        for i, key in enumerate(self.keywords):
            # 3. Take the full sequence of keyword
            sequence = key['keyword']
            # 4. Check if cluster already exists
            cluster = self.findCluster(sequence)
            if cluster == None:
                # 5. Check if any of the remaining keywords (i+1) contains the same sequence: 
                #    here it gets tricky: contains or starts with? What happens with the other keyword
                #    (it needs to be remove from the list to be processed, however it it start with 
                #    another keyword, we would prefer keywords by it's historic order which does not make sense)
                #    For now: compare = starts with
                while len(sequence) > 1:
                    for j in range(i+1, len(self.keywords)):
                        keyB = self.keywords[j]
                        if keyB['keyword'].startswith(sequence):
                            # 5.1. If yes, create new cluster
                            cluster = {
                                'keywords': [key, keyB],
                                'cluster': sequence,
                                'count': key['count'] + keyB['count']
                            }
                            self.clusters.append(cluster)
                            break
                # 6. If no, remove last word of sequence, repeat from 4.
                if cluster == None:
                    
                        sequence.pop()
                        cluster = self.findCluster(sequence)
                        if cluster != None:
                            break
                    # 7. If no cluster was found, add keyword to list of single keywords
                    if cluster == None:
                        singleKeywords.append(key)
                while len(sequence) > 1:
                    sequence.pop()
                    cluster = self.findCluster(sequence)
                    if cluster != None:
                        break
                # 7. If no cluster was found, add keyword to list of single keywords
                if cluster == None:
                    singleKeywords.append(key)
            else:
                # 8. If yes, create new cluster
                self.clusters.append({
                    'keywords': [key],
                    'cluster': cluster
                })
        
        return