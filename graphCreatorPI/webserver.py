from flask import Flask, render_template, request, jsonify
from GraphBuilder_Raw import GraphBuilderRAW
import json

app = Flask(__name__)

# Read Keyword data
file = open('out/graph.json', 'r')
root = json.loads(file.read())

print("... raw build graph")
graphRaw = GraphBuilderRAW(root['keywords'], root['publication'])
graphRaw.build()
graphRaw.removeKeywords(['product lifecycle management'])

def getTopKeywordsForYear(year, max):
    result = []
    for keyword in graphRaw.keywords:
        for y in keyword['years']:
            if int(y['year']) == int(year):
                result.append({
                    'keyword': keyword['keyword'],
                    'count': y['count'],
                    'change': 0,
                    'posdiv': 0
                })
    result.sort(key=lambda x: x['count'], reverse=True)
    return result[0: min(max, len(result))]

@app.route('/keywordsByYear/<year>')
def query(year): 
    result = {
        'top' : [],
        'out' : []
    }
    if 'max' in request.args:
        max = int(request.args['max'])
    else:
        max = 15
    result['top'] = getTopKeywordsForYear(year, max)
    #compare to year before
    preYear = str(int(year) - 1)
    last = getTopKeywordsForYear(preYear, max)
    for j, lastKeyword in enumerate(last):
        hit = False
        for i, keyword in enumerate(result['top']):
            if keyword['keyword'] == lastKeyword['keyword']:
                keyword['change'] = keyword['count'] - lastKeyword['count']
                keyword['posdiv'] = j - i
                hit = True
        if not hit:
            result['out'].append(lastKeyword)
    return jsonify(result)

app.run(debug=True, host='0.0.0.0', port=4000)