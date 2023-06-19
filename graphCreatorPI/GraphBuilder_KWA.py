import re
import json
import numpy as np
import matplotlib.pyplot as plt

class GraphBuilderKWA:

    def __init__(self, keywords, publications): 
        self.keywords = keywords
        self.publications = publications
        self.kwaTable = []
      
    def build(self):
        # loop through all publications
        # add edge for all keywords
        firstRow = ['id', 'year']
        for i, pub in enumerate(self.publications):
            row = [i, pub['year']]
            for key in self.keywords:
                if i==0:
                    firstRow.append(key['keyword'])
                for pubKey in pub['keywords']:
                    if pubKey == key['keyword']:
                        row.append(1)
                    else:   
                        row.append(0)
            if i==0:
                self.kwaTable.append(firstRow)
            self.kwaTable.append(row)
        return
    
    def write(self, filename):
        tableFile = filename + '.csv'

        #Node Table
        open(tableFile, 'w').close()
        file = open(tableFile, 'a')
        for row in self.kwaTable:
            rstr = ""
            for i, cell in enumerate(row):
                rstr += str(cell) + ";"
            file.write(rstr + "\n")
        file.close
        return