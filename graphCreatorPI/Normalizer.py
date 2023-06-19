import csv

class Normalizer:
    def __init__(self, normTableFile, logfile):
        self.normTableFile = normTableFile
        self.logfile = logfile
        self.keywords = []
        open(logfile, 'w').close()

    def readNormTable(self):
        self.normTable = []
        with open(self.normTableFile, newline='') as file:
            kwReader = csv.reader(file, delimiter=',')
            for row in kwReader:
                self.normTable.append(row)
        return self.normTable

    def readAcronyms():
        return

    def logMissingKeywords(self, keyword, title, year):
        file = open(self.logfile, 'a')
        file.write(keyword + "; " + title + "; " + str(year) + "\n")
        file.close

    def normalize(self, publications):
        missingKeywordCount = 0
        normTable = self.readNormTable()
        for pub in publications:
            normKeywords = []
            for keyword in pub['keywords']:
                #find normalized form
                check = False
                for row in normTable:
                    # check if keywords matches mapping in normalization or is already in normalized form
                    # trim keyword white space and convert to lower case
                    if row[0].lower() == keyword.strip().lower() or row[1] == keyword.strip().lower():
                        index = self.addOrWeightKeyword(row[1], pub['year'])
                        normKeywords.append(index)
                        check = True
                        break
                if check == False:
                    #print('Keyword not found: "' + keyword + '" in  "' + pub['title']+'"')
                    missingKeywordCount = missingKeywordCount + 1
                    self.logMissingKeywords(keyword, pub['title'], pub['year'])
            pub['keywords'] = normKeywords
        print ('    Quality report: Missing keywords: ' + str(missingKeywordCount))
        return publications

    def addOrWeightKeyword(self, keyword, year):
        index = -1
        for i, key in enumerate(self.keywords):
            if key['keyword'] == keyword:
                key['count'] = key['count'] + 1
                yearCount = -1
                for y in key['years']:
                    if y['year'] == year:
                        yearCount = y['count'] + 1
                        y['count'] = yearCount
                        break
                if yearCount == -1:
                    key['years'].append({ 'year' : year, 'count': 1})
                index = i
                break
        if index == -1:
            index = len(self.keywords)
            self.keywords.append({
                'keyword': keyword,
                'count': 1,
                'years': [{ 'year' : year, 'count': 1}]
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