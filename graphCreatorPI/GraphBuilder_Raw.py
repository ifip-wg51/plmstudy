import re
import json
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from datetime import date


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

    def createJsonEdges(self, edgeThreshold, blacklist):
        result = []
        for edge in self.edges:
            if edge['weight'] >= edgeThreshold:
                if not edge['A'] in blacklist and not edge['B'] in blacklist:
                    result.append({
                        'source' : self.keywords[edge['A']]['keyword'],
                        'target' : self.keywords[edge['B']]['keyword'],
                        'sourceID' : edge['A'],
                        'targetID' : edge['B'],
                        'weight' : edge['weight']
                    })
        return result

    def clusterByModularity(self, edges):
        G = nx.Graph()
        for edge in edges:
            G.add_edge(edge['sourceID'], edge['targetID'], weight=edge['weight'])
        communities = nx.algorithms.community.modularity_max.greedy_modularity_communities(G)
        return communities
    
    def addOnceFDGNode(self, list, keyword, gid, communities):
        group = -1
        for gn, community in enumerate(communities):
            if gid in community:
                group = gn
        node = {
                'id' : keyword['keyword'],
                'gid' : gid,
                'group' : group,
                'count' : keyword['count']
            }
        for item in list:
            if item['gid'] == node['gid']:
                return
        list.append(node)
        return
    
    def writeForceDirectedGraphJSON(self, filename, edgeThreshold, blacklist):
        graph = {
            'links' : self.createJsonEdges(edgeThreshold, blacklist),
            'nodes' : []
        }
        communities = self.clusterByModularity(graph['links'])
        for link in graph['links']:
            keyA = self.keywords[link['sourceID']]
            self.addOnceFDGNode(graph['nodes'], keyA, link['sourceID'], communities)
            keyB = self.keywords[link['targetID']]
            self.addOnceFDGNode(graph['nodes'], keyB, link['targetID'], communities)

        file = open(filename + '.json', 'w')
        file.write(json.dumps(graph, indent = 4))
        file.close()
        return
    
    def writeChordDiagramJSON(self, filename, edgeThreshold, blacklist):
        jsonData = json.dumps(self.createJsonEdges(edgeThreshold, blacklist), indent = 4) 
        file = open(filename + '.json', 'w')
        file.write(jsonData)
        file.close()
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
    
    def writeTopKeywords(self, filename, max, blacklist):
        result = []
        for i in range(2005,2024):
            res = self.getTopKeywordsForYear(str(i), max)
            for r in res:
                r['date'] = date(i, 1, 1).isoformat()
                result.append(r)
        jsonData = json.dumps(result, indent = 4) 
        file = open(filename + '.json', 'w')
        file.write(jsonData)
        file.close()
        return result

    def getTopKeywordsForYear(self, year, max):
        result = []
        for keyword in self.keywords:
            for y in keyword['years']:
                if int(y['year']) == int(year):
                    result.append({
                        'name': keyword['keyword'],
                        'value': y['count'],
                        'change': 0,
                        'posdiv': 0
                    })
        result.sort(key=lambda x: x['value'], reverse=True)
        return result[0: min(max, len(result))]

    def removeKeywords(self, labels):
        for keyword in self.keywords:
            if keyword['keyword'] in labels:
                self.keywords.remove(keyword)
        return