import requests

isbns = [
    "978-3-642-35758-9", #2012
    "978-3-642-41501-2", #2013
    "978-3-662-45937-9", #2014
    "978-3-319-33111-9", #2015
    "978-3-319-54660-5", #2016
    "978-3-319-72905-3", #2017
    "978-3-030-01614-2", #2018
    "978-3-030-42250-9", #2019
    "978-3-030-62807-9", #2020
    "978-3-030-94335-6", #2021
    "978-3-031-25182-5", #2022
]

def getSpringerAPI(isbn):
    url = 'http://api.springernature.com/meta/v2/json?q=isbn:' + isbn + '&p=100&api_key=93347ea55743e63a222615f3af8dce2f'
    print(url)
    response = requests.get(url)
    data = response.json()
    # print(data)
    pubs=[]
    for pub in data['records']:
        if 'keyword' in pub.keys():
            pubs.append({
                'title': pub['title'],
                'keywords': pub['keyword'],
                'year':  pub['publicationDate'][0:4]
            })
    return pubs

def read():
    publications = []
    print("Start reading IC PLM input Data")
    print("  ... get content from Springer API")
    for isbn in isbns:  
        pubs = getSpringerAPI(isbn)
        print('isbn: ' + isbn + ' count: ' + str(len(pubs)))
        publications.extend(pubs)
    # add manual content here
    print("Done reading")
    return publications

