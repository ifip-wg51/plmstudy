/*
  Main file of plmgraphs
  This creates an express webserver and routs all requiered Services the retrieve the
  data form the database.

  @author Felix Nxffenegger
  @author Christian Braesch
  @author Louis Rivest
*/

var regression = require('./public/js/lib/regression.js');
var express = require('express');
var sqlite3 = require('sqlite3').verbose();
var util = require('util');
var fs = require('fs');
var basicAuth = require('basic-auth-connect');

/*********************************************************************
  Global constants
**********************************************************************/

/* The GEXF File is cerated with Gephi and stores the initial positions
   of all nodes and statisitical data that was calculated with Gephi */
var pathGEXF = '/data/plmgraph.gexf';

/* The Database is the product of processing the raw data from Zotero 
   and all normalization files. 
   @TODO: Replace this by an array, so multpile databases can be accessed
*/
var pathAnalysisDB = '/../database/PLM_analysis.sqlite';
/* GeoJSON Data for Countries 
   Data borrowed from: https://github.com/johan/world.geo.json*/
var pathGeoJSON = '/maps/countries.geo.json';

/* Defaults */
var defaultMinYear = 2004;
var defaultMaxYear = 2014;

/**********************************************************************
  Setup Webserver and Authentication
**********************************************************************/
var app = express();

/* Route alle /public request as static */
app.use('/', express.static(__dirname + '/public'));

/* Very simple authentication :-) */
app.use(basicAuth(function(user, pass){
  return ('plmstudy' == user && 'amarok' == pass) || 
         ('PLM16' == user && 'iAttended' == pass);
}));

/**********************************************************************
  Webservices (Rouring and Implementation)
**********************************************************************/

/* Get the GEXF data*/ 
app.get('/data/gexf', function (req, res) {
  res.sendFile(__dirname + pathGEXF);
});


/* Get Gephy JSON data (just for test) */
app.get('/data/keywordgraph', function (req, res) {
  res.sendFile(__dirname + '/data/keywordgraph.json');
});

/* 
  Claculate histogram and trend for a specific keyword by ID 
  @param tagID ID of the keyword 
*/
app.get('/data/keyword/histogram/:tagID', function (req, res) {
  var tagID = req.params.tagID;
  var db = new sqlite3.Database(__dirname + pathAnalysisDB);
  db.serialize(function () {
    var results = {
      years : []
    };
    var query = 'SELECT pubYear, COUNT(*) AS cnt FROM publicationTags NATURAL JOIN publications WHERE tagID='+tagID+' GROUP BY pubYear ORDER BY pubYear;';
    db.each(query, function (err, row) {
      results.years.push({
        'year' : row.pubYear,
        'count' : row.cnt
      });
     }, function() {
      res.json(results);
    });
  });
  db.close();
});

/* 
  Get the the list of publications for a specific keyword by ID
  @param tagID ID of the keyword 
*/
app.get('/data/keyword/publications/:tagID', function (req, res) {
  var tagID = req.params.tagID;
  var db = new sqlite3.Database(__dirname + pathAnalysisDB);
  db.serialize(function () {
    var results = [];
    var query = 'SELECT pubID, pubTitle, pubYear, pubSource FROM publicationTags NATURAL JOIN publications WHERE tagID='+tagID+' ORDER BY pubYear;';
    db.each(query, function (err, row) {
      results.push({
        'id' : row.pubID,
        'title' : row.pubTitle,
        'year' : row.pubYear,
        'source' : row.pubSource
      });
     }, function() {
      res.json(results);
    });
  });
  db.close();
});

/* 
  Get the the list of publications for a specific keyword by ID
  @param x Number of results
*/
app.get('/data/keyword/trends/top/:x', function (req, res) {
  var x = req.params.x;
  var db = new sqlite3.Database(__dirname + pathAnalysisDB);
  db.serialize(function () {
    var results = []
    var query = 'SELECT tagID, tagName, pubYear, COUNT(*) AS cnt FROM tags NATURAL JOIN publicationTags NATURAL JOIN publications GROUP BY pubYear, tagID ORDER BY tagID;';
    var tagID = -1;
    var years = [];
    var tagName = "";
    db.each(query, function (err, row) {
      if (tagID == -1) {
        tagID = row.tagID;
        tagName = row.tagName;
      }
      if (row.tagID == tagID) {
        // add year to years array
        years.push({
          'year' : row.pubYear,
          'count' : row.cnt
        });
      }
      else {
        if (tagID >= 0) {
          if (years.length > 1) {
            //var rx = [];
            //var ry = [];
            var data = [];
            var year = 2005;
            for (var i = 0; i < 10; i++) {
              var exists = false;
              for(y in years) {
                if (years[y].year == year) {
                  //rx.push(years[y].year);
                  //ry.push(years[y].count);
                  data.push([years[y].year, years[y].count]);
                  exists = true;
                }
              }
              if (!exists) {
                //rx.push(year);
                //ry.push(0);
                data.push([years[y].year, years[y].count]);
                years.push({
                  'year' : year,
                  'count' : 0
                })
              }
              year++;
            }
            //var reg = UTILS.linearRegression(rx,ry);
            var reg = regression('linear', data);
            results.push({
              'id' : tagID,
              'name' : tagName,
              'years' : years,
              //'slope' : reg.slope,
              'slope' : reg.equation[0],
              //'intercept' : reg.intercept,
              'intercept' : reg.equation[1],
              'r2' : reg.r2
            })
          }
        }
        years =[];
        tagID = row.tagID;
        tagName = row.tagName;
      }
     }, function() {
      results.sort(function(obj1, obj2) {
        // Ascending: first age less than the previous
        // first order slope desceing
        var res = obj2.slope - obj1.slope;
        if (res == 0) {
          // second order r2 descending
          res = obj2.intercept - obj1.intercept;
        }
        return res;
      });
      res.json(results);
    });
  });
  db.close();
});

/*
  Inject the Metadata of our Database into the GeoJSON data
*/
app.get('/data/get/geojson/metadata', function (req, res) {
  var db = new sqlite3.Database(__dirname + pathAnalysisDB);
  var file = fs.readFileSync(__dirname + pathGeoJSON, 'utf-8');
  var geodata = JSON.parse(file);

  // Evaulate request for optional year data
  var minYear = defaultMinYear;
  var maxYear = defaultMaxYear;
  db.serialize(function () {
    var results = {
      'type':'FeatureCollection',
      'features':[]
    };
    var last = null;
    var totalCount = 0;
    var query = 'SELECT couID, couName, pubYear, couLongitude, couLatitude, COUNT(*) AS cnt FROM publications NATURAL JOIN countries WHERE pubYear > ' + minYear + ' AND pubyear < ' + maxYear + ' GROUP BY couName, pubYear ORDER BY couID;'
    var found = false;
    
    //console.log(req.query.filter);

    db.each(query, function (err, row) {
      var country = null;

      if (last == null || row.couName != last.properties.name) {
        
        if (last != null) {
          last.properties.count = totalCount;
          totalCount = 0;
        }
        var country = null;
        for(c in geodata.features) {
          country = geodata.features[c];
          if (country.properties.name == row.couName) {
            country.properties.years = [{
              'year' : row.pubYear,
              'count' : row.cnt
            }];
            country.properties.id = row.couID;
            totalCount = row.cnt;
            results.features.push(country);
            found = true;
            break;
          }
        }
        if (!found) {
          //console.log("Country not found: " + row.couName);
          //Add it to the output as point feature
          country = {
            'type' : 'Feature',
            'id'   :  'C' + row.couID,
            'geometry' : {
              'type' : 'Polygon',
              'coordinates' : [[
                [row.couLongitude-0.5 , row.couLatitude-0.5], 
                [row.couLongitude-0.5 , row.couLatitude+0.5], 
                [row.couLongitude+0.5 , row.couLatitude+0.5], 
                [row.couLongitude+0.5 , row.couLatitude-0.5], 
                [row.couLongitude-0.5 , row.couLatitude-0.5] 
              ]]
            },
            'properties' : {
              'name'  : row.couName,
              'id'    : row.couID,
              'years' : [{
                'year'  : row.pubYear,
                'count' : row.cnt
              }]
            }
          };
          totalCount = row.cnt;
          results.features.push(country);
        }
      } else {
       
        country = last;
        country.properties.years.push({
          'year' : row.pubYear,
          'count' : row.cnt
        });
        totalCount += row.cnt;
      }
      //console.log(row.couName + " : " + row.pubYear + " : " + row.cnt + "(" + totalCount +")");
      last = country;
    }, function() {
      last.properties.count = totalCount;
      res.json(results);
    });
  });

  db.close();
});

app.get('/data/get/geojson/countries', function (req, res) {
  res.sendFile(__dirname + '/maps/countries.geo.json');
});

/*
  Get basic Information about our database
*/
app.get('/data/get/basicdata', function (req, res) {
  var db = new sqlite3.Database(__dirname + pathAnalysisDB);
  // Evaulate request for optional year data
  var minYear = defaultMinYear;
  var maxYear = defaultMaxYear;
  
  db.serialize(function () {
    var results = {};
    db.get('SELECT COUNT(*) as cnt FROM publications WHERE pubYear > ' + minYear + ' AND pubyear < ' + maxYear + ';', function (err, row) {
      results.pubCount = row.cnt;
    });
    db.each('SELECT pubType, COUNT(*) as cnt FROM publications WHERE pubYear > ' + minYear + ' AND pubyear < ' + maxYear + ' GROUP BY pubType;', function (err, row) {
      if (row.pubType == 'conferencePaper') {
        results.pubConfCount = row.cnt;
      }
      if (row.pubType == 'journalArticle') {
        results.pubJournalCount = row.cnt;
      } 
    });
    results.topConfs = [];
    db.all('SELECT pubSource, COUNT(*) as cnt FROM publications WHERE pubYear > ' + minYear + ' AND pubyear < ' + maxYear + ' AND pubType = "conferencePaper" GROUP BY pubSource ORDER BY cnt DESC;', function (err, rows) {
      for (var i = 0; i<3; i++) {
        var row = rows[i];
        results.topConfs[i] = {
          'name' : row.pubSource,
          'count' : row.cnt
        }
      }  
    });
    results.topJournals = [];
    db.all('SELECT pubSource, COUNT(*) as cnt FROM publications WHERE pubYear > ' + minYear + ' AND pubyear < ' + maxYear + ' AND  pubType = "journalArticle" GROUP BY pubSource ORDER BY cnt DESC;', function (err, rows) {
      for (var i = 0; i<3; i++) {
        var row = rows[i];
        results.topJournals[i] = {
          'name' : row.pubSource,
          'count' : row.cnt
        }
      }  
    });
    db.get('SELECT COUNT(DISTINCT pubSource) as cnt FROM publications WHERE pubYear > ' + minYear + ' AND pubyear < ' + maxYear + ' AND pubType = "conferencePaper";', function (err, row) {
      results.confCount = row.cnt;
    });
    db.get('SELECT COUNT(DISTINCT pubSource) as cnt FROM publications WHERE pubYear > ' + minYear + ' AND pubyear < ' + maxYear + ' AND pubType = "journalArticle";', function (err, row) {
      results.journalCount = row.cnt;
    });
    db.get('SELECT COUNT(DISTINCT tagID) as cnt From tags NATURAL JOIN publicationTags NATURAL JOIN publications WHERE pubYear > ' + minYear + ' AND pubyear < ' + maxYear + ' ORDER BY tagID;', function (err, row) {
      results.tagCount = row.cnt;

      // Send result after last query
      res.json(results);
    });
   
  });
  db.close();
});

/**********************************************************************
  Start teh webserver on Port 8080
**********************************************************************/

var server = app.listen(8080, function () {
  var host = server.address().address;
  var port = server.address().port;

  console.log('Example app listening at http://%s:%s', host, port);
});

/*
      if (err != null) {
        console.log(err);
      }
*/