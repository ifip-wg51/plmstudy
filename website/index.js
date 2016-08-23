/*
  Main file of plmgraphs
*/

var express = require('express');
var sqlite3 = require('sqlite3').verbose();
var util = require('util');
var app = express();

app.use('/', express.static(__dirname + '/public'));


app.get('/data/test', function (req, res) {
  res.sendFile(__dirname + '/data/test.json');
});

app.get('/data/keywordgraph', function (req, res) {
  res.sendFile(__dirname + '/data/keywordgraph.json');
});

/*
  Select Data for Co-Occurrence Graph of Keywords occurring on the same papers
*/
app.get('/data/create/keywordgraph', function (req, res) {
  var db = new sqlite3.Database('data/zotero.sqlite');
  var results = {};

  var idInArray = function (a, id) {
    for (var i = 0; i < a.length; i++) {
        if (a[i].id == id) {
          return true;
        }
    }
    return false;
  }

  db.serialize(function () {
    var i = 0,
        e = 0,
        x = 1,
        y = 1;
    var nodes = [];
    var edges = [];
    var cc = 0;
    var kc = 0;
    db.all('SELECT DISTINCT tagID, name, COUNT(itemID) as frequency \
    FROM tags NATURAL JOIN itemTags \
    WHERE name NOT LIKE "COUNTRY_%" \
    LIMIT 1000 \
    GROUP BY tagID ORDER BY name;', function (err, rows) {
      for (var n in rows) {
        var row = rows[n];
        // Create Graph Objects
        nodes[i] = {
          'id' : row.tagID.toString(),
          'label' : row.name,
          'x' : Math.random(),
          'y': Math.random(),
          'size' : row.frequency
        };
        i++;
        x++
        if (x > 20) {
          y++
          x = 1;
        }
      }

      kc = nodes.length;
      for (var n in nodes) {
        // find co-occurrences for this node
        // WHERE source.tagID = ' + nodes[n].id + ' \
        db.all('SELECT DISTINCT source.tagID as sourceID, target.tagID as targetID, COUNT(target.tagID) as count FROM itemTags source \
        INNER JOIN itemTags target ON source.itemID = target.itemID \
        WHERE source.tagID = ' + nodes[n].id + ' \
        GROUP BY target.tagID;', function (err, rows) {
          for (var r in rows) {
            var trow = rows[r];
            if ((trow.sourceID != trow.targetID) && idInArray(nodes, trow.targetID)) {
              edges[e] = {
                'id' : 'e' + e.toString(),
                'source' : trow.sourceID.toString(),
                'target' : trow.targetID.toString()
              };
              e++;
            }
          }
          // Send response if last callback is done
          cc++;
          if (cc == kc) {
            db.close();
            console.log('Exportet ' + kc + 'Keyword Nodes');
            console.log('Exportet ' + e + 'Co-Occurrence Edges');
            results.nodes = nodes;
            results.edges = edges;
            res.json(results);
          }
        });
      }
    });
  });
});

var server = app.listen(3000, function () {
  var host = server.address().address;
  var port = server.address().port;

  console.log('Example app listening at http://%s:%s', host, port);
});