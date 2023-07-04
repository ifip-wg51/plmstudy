import re
import json
import numpy as np
import matplotlib.pyplot as plt
import copy

class GraphBuilderWordTree:

    def __init__(self, keywords, publications): 
        self.keywords = keywords
        self.publications = publications
        self.nodeEdges = []
        self.nodelist = []
        self.rootNode = {}
        self.threshold = 5
        self.nodeId = 0
        self.depth = 3

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


    def addNode(self, label, keywords, count, parent):
        node =  {
            'id' : self.nodeId,
            'label' : label,
            'count': count,
            'keywords' : keywords,
            'nodes': [],
            'years': [],
            #'parent' : parent
        }
        self.nodelist.append(node)
        self.nodeId += 1
        if parent != None:
            parent['nodes'].append(node)

        return node

    def condenseByCommonWordsRecursive(self, node, level = 0):
        nodeFound = False
        # find all keywords that are strong enough to be a node
        for keyA in node['keywords']:
            if keyA['count'] > self.threshold:
                if not 'node' in keyA:
                    newNode = self.addNode(keyA['keyword'], [ keyA ], keyA['count'], node)
                    keyA['node'] = newNode
                    node['keywords'].remove(keyA)
                    nodeFound = True

        for keyA in node['keywords']:
            matches = []
            count = 0
            words = keyA['keyword'].split(" ")
            if len(words) > level:
                word = " ".join(words[:level+1])
                if len(word) > 0:
                    # special case for "in", "of" and "product" to avoid "production as part of product" as a node
                    if word in ['in','of','product']:
                        word = " ".join(words[:level+1]) + " "
                    for keyB in node['keywords']:
                        if keyB != keyA and keyB['keyword'].startswith(word):
                            matches.append(keyB)
                            count += keyB['count']
                    if count > self.threshold:
                        newNode = self.addNode(word+ " ...", matches, -1, node)
                        self.nodeId += 1
                        for match in matches:
                            node['keywords'].remove(match)
                            match['node'] = newNode
                        nodeFound = True
        if nodeFound & level < self.depth:
            for subNode in node['nodes']:
                self.condenseByCommonWordsRecursive(subNode, level+1)
        return
    
    def removeNodes(self, labels):
        for node in self.nodelist:
            if node['label'] in labels:
                self.nodelist.remove(node)
        return
    
    def buildNodeEdges(self, publications):
        self.nodeEdges = []
        for pub in publications:
            for i, pubKeyA in enumerate(pub['keywords']):
                # only compare forward in the array (i+1) to avoid A = B and B = A (edges have no direction)
                for j in range(i+1, len(pub['keywords'])):
                    pubKeyB = pub['keywords'][j]
                    if pubKeyA != pubKeyB:
                        if 'node' in self.keywords[pubKeyA]:
                            if 'node' in self.keywords[pubKeyB]:
                                nodeA = self.keywords[pubKeyA]['node']
                                nodeB = self.keywords[pubKeyB]['node']
                                self.addOrWeightEdge(self.nodeEdges, nodeA['id'], nodeB['id'])
        #remove circular reference for json export
        for keyword in self.keywords:
            if 'node' in keyword:
                del keyword['node']
        return

    def updatedCountsRecursive(self, node):
        count = 0
        for key in node['keywords']:
            count += key['count']
            for y in key['years']:
                check = False
                for y2 in node['years']:
                    if y['year'] == y2['year']:
                        y2['count'] += y['count']
                        check = True
                if not check:
                    node['years'].append(y)
        node['count'] = count
        for subNode in node['nodes']:
            self.updatedCountsRecursive(subNode)
        return

    def build(self, threshold, depth=3):
        # 1. Create rootNode
        # 2. Clone list of keywords and add it to rootNode
        # 3. for each node
        # 4. for all keywords in the node
        # 5.   if keyword count is higher than threshold create a subnode with just this keyword
        #       and remove the keyword from the node
        # 6.   else find all keywords that start with the same i words
        # 7.     if count of keywords found is higher than threshold:
        # 8.       add all keywords to a new subnode
        # 9.       remove these keywords from the node
        # 10.    else, keep keyword in node
        # 11. repeat from 9 for all subnodes until no further subnodes are found
        self.nodeEdges = []
        self.nodeId = 0
        self.nodelist = []
        self.threshold = threshold
        self.depth = depth
        self.rootNode = {}
        keywords = copy.deepcopy(self.keywords)
        rootNode = self.addNode('ICPLM', keywords, 0, None)
        self.nodelist.remove(rootNode)
        self.rootNode = rootNode
        self.condenseByCommonWordsRecursive(rootNode, 0)
        self.updatedCountsRecursive(rootNode)
        self.buildNodeEdges(self.publications)
        return
    
################################################################
#   Methods for output
    
    def writeJSON(self, filename):
        jsonNodeTree = json.dumps(self.rootNode, indent = 4)
        jsonNodeEdges = json.dumps(self.nodeEdges, indent = 4) 
        file = open(filename + '.json', 'w')
        file.write(jsonNodeTree)
        file.close()
        file = open(filename + '_edges.json', 'w')
        file.write(jsonNodeEdges)
        file.close()
        return
    
    def collectSunburstDataRecursive(self, node, level):
        if node['label'] == 'product lifecycle management':
            return None
        treeNode = {
            'name' : node['label'],
            'value' : node['count'],
            'children' : []
        }
        for subNode in node['nodes']:
            newNode = self.collectSunburstDataRecursive(subNode, level + 1)
            if newNode != None:
                treeNode['children'].append(newNode)
        if level > 0:
            for keyword in node['keywords']:
                if keyword['keyword'] != node['label']:
                    treeNode['children'].append({
                        'name' : keyword['keyword'],
                        'value' : keyword['count'],
                        'children' : []
                    })
        return treeNode

    def writeSunburstJSON(self, filename):
        treeRoot = self.collectSunburstDataRecursive(self.rootNode, 0)
        jsonTree = json.dumps(treeRoot, indent = 4) 
        file = open(filename + '.json', 'w')
        file.write(jsonTree)
        file.close()
        return
    
    def getNodeByID(self, id):
        for node in self.nodelist:
            if node['id'] == id:
                return node


    def writeChordDiagramJSON(self, filename):
        result = []
        for edge in self.nodeEdges:
            if edge['weight'] > 2:
                result.append({
                    'source' : self.getNodeByID(edge['A'])['label'],
                    'target' : self.getNodeByID(edge['B'])['label'],
                    'value' : edge['weight']
                })
        jsonData = json.dumps(result, indent = 4) 
        file = open(filename + '.json', 'w')
        file.write(jsonData)
        file.close()
        return
    
    def writeGephi(self, filename):
        #Node Table
        
        open(filename + '.csv', 'w').close()
        file = open(filename+ '.csv', 'a')
        file.write("Id;Label;Timestamp;Count;Time_count\n")
        for node in self.nodelist:
            timeInterval = "<["
            countInterval = "<"
            for y in node['years']:
                timeInterval += str(y['year']) + ","
                countInterval += "[" + str(y['year']) + "," + str(y['count']) + "]"
            timeInterval += "]>"
            countInterval += ">"
            file.write(str(node['id']) + ";" + node['label'] + ";" + timeInterval +  ";" + str(node['count']) + ";" + countInterval + "\n")
        file.close

        #Edge Table
        open(filename + '_edges.csv', 'w').close()
        file = open(filename + '_edges.csv', 'a')
        file.write("Source;Target;Type;Weight\n")
        for edge in self.nodeEdges:
            file.write(str(edge['A']) + ';' + str(edge['B']) + ';Undirected;' + str(edge['weight']) + "\n")
        file.close
        return
    
    def writeIgnoredKeywords(self, filename):
        open(filename, 'w').close()
        file = open(filename, 'a')
        file.write("keyword;count\n")
        for keyword in self.rootNode['keywords']:
            file.write(keyword['keyword'] + ";" + str(keyword['count']) + "\n")
        file.close
        return

    def plotNodes(self, filename, show=True):
        labels = []
        counts = []
        for i,node in enumerate(self.nodelist):
            labels.append(i)
            counts.append(node['count'])
        counts.sort(reverse=True)
        plt.plot(labels, counts)
        plt.xlabel("keywords")
        plt.ylabel("count")
        plt.title("l-shaped histogram (" + str(len(labels)) + " nodes, " + str(len(self.rootNode['keywords'])) + " ignored)")
        plt.ylim(0, 50)
        plt.xlim(0, 200)
        if show:
            plt.show()
        else:
            plt.savefig(filename)
        plt.close()
        return { 'nodes': len(labels), 'ignored': len(self.rootNode['keywords'])}


