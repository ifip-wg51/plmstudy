import re
import json
import numpy as np
import matplotlib.pyplot as plt

class GraphBuilderRAW:

    def __init__(self, keywords, publications): 
        self.keywords = keywords
        self.publications = publications
        self.edges = []
      
    def addOrWeightEdge(self, list, idA, idB):
        index = -1
        for i, edge in enumerate(list):
            #check for both directions
            if (edge['A'] == idA and edge['B'] == idB) or (edge['A'] == idB and edge['B'] == idA):
                edge['weight'] = edge['weight'] + 1
                index = i
                break
        if index == -1:
            index = len(list)
            list.append({
                'A': idA,
                'B': idB,
                'weight': 1
            })
        return index

    def build(self):
        # loop through all publications
        # add edge for all keywords
        for pub in self.publications:
            for i, pubKeyA in enumerate(pub['keywords']):
                # only compare forward in the array (i+1) to avoid A = B and B = A (edges have no direction)
                for j in range(i+1, len(pub['keywords'])):
                    pubKeyB = pub['keywords'][j]
                    if pubKeyA != pubKeyB: #not necessary since wi iterate from i+1
                        self.addOrWeightEdge(self.edges, pubKeyA, pubKeyB)
        return
    
    def writeGephi(self, filename):
        keywordFile = filename + '.csv'
        edgeFile = filename + '_edges.csv'

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

    def plotKeywords(self, filename, xlim, ylim, show=True):
        labels = []
        counts = []
        self.keywords.sort(key=lambda x: x['count'], reverse=True)
        for i,k in enumerate(self.keywords):
            labels.append(i)
            counts.append(k['count'])
        plt.plot(labels, counts)
        plt.xlabel("keywords")
        plt.ylabel("count")
        plt.title("l-shaped histogram (" + str(len(labels)) + " keywords)")
        plt.ylim(0, ylim)
        plt.xlim(0, xlim)

        if show:
            plt.show()
        else:
            plt.savefig(filename)
                    
        plt.close()
        return
    
    def removeKeywords(self, labels):
        for keyword in self.keywords:
            if keyword['keyword'] in labels:
                self.keywords.remove(keyword)
        return