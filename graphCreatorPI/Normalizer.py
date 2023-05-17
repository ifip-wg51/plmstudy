import csv

##Todo: Handle Acronyms

class Normalizer:
    def __init__(self, normTableFile, logfile):
        self.normTableFile = normTableFile
        self.logfile = logfile
        self.keywords = []

    def readNormTable(self):
        self.normTable = []
        with open(self.normTableFile, newline='') as file:
            kwReader = csv.reader(file, delimiter=';')
            for row in kwReader:
                self.normTable.append(row)
        return self.normTable

    def readAcronyms():
        return

    def logMissingKeywords(self, keyword):
        file = open(self.logfile, 'a')
        file.write(keyword+"\n")
        file.close

    def normalize(self, publications):
        normTable = self.readNormTable()
        for pub in publications:
            normKeywords = []
            for keyword in pub['keywords']:
                #find normalized form
                check = False
                for row in normTable:
                    if row[0].lower() == keyword.lower():
                        #lookup acronyms with multiple meanings
                        index = self.addOrWeightKeyword(row[1])
                        normKeywords.append(index)
                        check = True
                        break
                if check == False:
                    print('Keyword not found: "' + keyword + '" in  "' + pub['title']+'"')
                    self.logMissingKeywords(keyword)
            pub['keywords'] = normKeywords
        return publications

    def addOrWeightKeyword(self, keyword):
        index = -1
        for i, key in enumerate(self.keywords):
            if key['keyword'] == keyword:
                key['count'] = key['count']+1
                index = i
                break
        if index == -1:
            index = len(self.keywords)
            self.keywords.append({
                'keyword': keyword,
                'count': 1
            })
        return index

    def getKeywordByID(self, id):
        return self.keywords[id]['keyword']
    
    def writePublications(self, filename, publications):
        open(filename, 'w').close()
        file = open(filename, 'a')
        for i, pub in enumerate(publications):
            file.write(str(i) + ';' + str(pub['title']) + ';')
            for key in pub['keywords']:
                file.write(self.keywords[key]['keyword'] + ';')
            file.write("\n")
        file.close