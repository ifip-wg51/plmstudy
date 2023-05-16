import requests

isbns = [
    "978-3-031-25182-5",
    "978-3-030-94335-6",
    "978-3-030-62807-9"
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
        data = getSpringerAPI(isbn)
        print('isbn: ' + isbn + ' count: ' + str(len(data)))
        publications.append(data)
    # add manual content here
    print("Done reading")
    return publications

