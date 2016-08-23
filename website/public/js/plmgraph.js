/*
  This Application shows the keywords in their coocurrency context 
*/

var APP = function() {
  function init() {
    // Fixes/Enhancements to 3rd party libraryies
    extend();

    // Instances and declarations
    var sigInst;
    var edgeColor = "rgba(180,180,180,0)"
    var mode = 0;
    
    // UI Events
    $('#stopLayout').click(function() {
      sigInst.stopForceAtlas2();
    });

    $('#startLayout').click(function() {
      startLayout();
    });
    

    $('#initial').click(function() {
      $('#container').empty();
      loadInitalGraph();
    });


    $('#showHideEdges').click(function(e) {
      if (sigInst != null) {
        if (e.target.innerHTML == "Show Edges") { 
          edgeColor = "rgba(180,180,180,0.5)";
          e.target.innerHTML = "Hide Edges";
        } else {
          edgeColor = "rgba(180,180,180,0)";
           e.target.innerHTML = "Show Edges";
        }
        sigInst.graph.edges().forEach(function(e) {
          e.color = edgeColor;
        });
        sigInst.refresh();
      }
    });

    $("#search").keyup(function (e) { 
      var code = (e.keyCode ? e.keyCode : e.which);

      if(code == 13) {
        setDefaultGraph();
        sigInst.graph.nodes().forEach(function(n) {
          if (n.label.search(e.target.value) >= 0) {
            n.label = n.originalLabel;
            n.color = '#028090';

          } else {
            n.label = "";
          }
        });
        sigInst.settings({ labelThreshold : 0 });
        sigInst.refresh();
      }
    });
    

    $('#filter').click(function () {
      filter();
    })
    ///////////////////////////////////////////////
    // Private mthods
    var startLayout = function () {    
      sigInst.startForceAtlas2({
        scalingRatio : 1000,
        startingIterations : 10,
        iterationsPerRender : 1,
        strongGravityMode : true,
        outboundAttractionDistribution : false,
        linLogMode : false,
        barnesHutOptimize : true,
        gravity : 1,
        adjustSizes : true
      });
      setTimeout(sigInst.stopForceAtlas2, 5000);
    }

    /*
     * Remove all nodes having a degree higher then "level"
     */
    var filter = function(minFilter, minValue, maxFilter, maxValue) {
      var removed;
      var maxValue = $('#max_value')[0].value;
      var minValue = $('#min_value')[0].value;
      var maxFilter = $('#filter_max')[0].value;
      var minFilter= $('#filter_min')[0].value;

      var node = sigInst.graph.nodes()[0];
      if (node.attributes[minFilter] != undefined && node.attributes[maxFilter] != undefined ) {
        sigInst.graph.nodes().forEach(function(n) {
          removed = false;
          if (minValue != "" && n.attributes[minFilter] <= parseInt(minValue)) {
            sigInst.graph.dropNode(n.id);
            removed = true;
          }
          if (removed==false) {
            if (maxValue != "" && n.attributes[maxFilter] >= parseInt(maxValue)) {
              sigInst.graph.dropNode(n.id);
            }
          }  
        });
      }
      sigInst.refresh();
    } 

    /* 
     * Progrssively load the history data for all keywords and add
     * the 50 most trendy to a table
     */
    var loadTrends = function() {
      // pull all trends for keywords and add them to the table as they come aling
      $.ajax({
        url: "data/keyword/trends/top/50", 
        success: function(result) {
          // populate table
          var i = 0;
          $('#trends > tbody').empty();
          for (r in result) {
            var res = result[r];
            var node = sigInst.graph.nodes(String(res.id));
            if (node != undefined) {
              node.attributes.slope = res.slope;
              node.attributes.intercept = res.intercept;
              node.attributes.r2 = res.r2;
              if (i < 50) {
                $('#trends > tbody:last-child').append('<tr><td>'+
                  res.id + '</td><td>' + 
                  res.name + '</td><td>' + 
                  round(res.slope, 4) + '</td><td>' + 
                  round(res.intercept, 0) + '</td>' +
                  //'<td>' + round(res.r2, 4) + '</td>'
                  '</tr>');
                i++;
              }
            } else {
              console.log("Node not found: " + res.id);
            }
          }
        }
      });
    }

    var round = function(num, digits) {
      return Math.round(num * Math.pow(10, digits)) / Math.pow(10, digits);
    }

    var loadNodeMesure = function(attribute) {
      
      var items = []
      sigInst.graph.nodes().forEach(function(n) {
        items.push(n);
      });
      items.sort(function (obj1, obj2) {
        return obj2.attributes[attribute] - obj1.attributes[attribute];
      });
      $('#network_data > tbody').empty();
      for (var i = 0; i < 50; i++) {
            var item = items[i];

            $('#network_data > tbody:last-child').append('<tr><td>'+
              item.id + '</td><td>' + 
              item.label + '</td><td>' + 
              item.attributes.degree + '</td><td>' + 
              round(item.attributes.eigencentrality, 3) + '</td><td>' + 
              round(item.attributes.betweenesscentrality, 3) + '</td></tr>');
          }
    }

    /* 
     * Create a grpah object and show the statistcal data about the
     * graph such as degree or betweenness 
     */
    var showGraphStats = function() {
      // Degree
      $('#key_degree')[0].innerHTML = "";
      var canvas = $('<canvas id="infochart" height="300" width="800"></canvas>').appendTo('#key_degree');
      var ctx = canvas.get(0).getContext("2d");
      var barChartData = {
        labels : [],
        datasets : [
            {
                label : "Degree",
                fillColor : "rgba(151,187,205,0.5)",
                strokeColor : "rgba(151,187,205,0.8)",
                highlightFill : "rgba(151,187,205,0.75)",
                highlightStroke : "rgba(151,187,205,1)",
                data : []
            }
        ]
      }
      sigInst.graph.nodes().forEach(function(n) {
        barChartData.labels.push("");
        barChartData.datasets[0].data.push(n.attributes.degree)
      });
      var chart = new Chart(ctx).Bar(barChartData, {
        //Number - Pixel width of the bar stroke
        barStrokeWidth : 1,
        //Number - Spacing between each of the X value sets
        barValueSpacing : 1,
      });
      ChartMethods.sort(chart, 0);
    }

    var setDefaultGraph = function() {
      sigInst.graph.nodes().forEach(function(n) {
          n.color = n.originalColor;
          n.label = n.originalLabel;
      });
      if (mode == 0) {
        sigInst.graph.edges().forEach(function(e) {
          e.color = edgeColor;
        });
        sigInst.settings({ labelThreshold : 4 });
      } 
      if (mode == 1) {
        sigInst.settings({ labelThreshold : 0 });
      }
      sigInst.refresh();
    }

    var loadInitalGraph = function() {
      sigInst = new sigma({
        renderer: {
          container: document.getElementById('container'),
          type: 'canvas'
        },
        settings : {
          defaultLabelColor: '#333',
          defaultLabelSize: 12,
          defaultLabelBGColor: '#000',
          defaultLabelHoverColor: '#000',
          labelThreshold: 8,      
          defaultEdgeColor: '#eee',
          minNodeSize: 1,
          maxNodeSize: 12,
          minEdgeSize: 0.5,
          maxEdgeSize: 5
        }
      });
        // Parse a GEXF encoded file to fill the graph
      // (requires "sigma.parseGexf.js" to be included)
      sigma.parsers.gexf('/data/gexf', sigInst, function(s) {
        // We first need to save the original colors of our
        // nodes and edges, like this:
        s.graph.nodes().forEach(function(n) {
          n.originalColor = n.color;
          n.originalLabel = n.label;
        });
        s.graph.edges().forEach(function(e) {
          s.graph.edges().forEach(function(ec) {
            // remove reverse connections if present
            if (e.source == ec.target && e.target == ec.source) {
              s.graph.dropEdge(ec.id);
            }
          });
          e.color = edgeColor;
          e.originalColor = e.color;
          e.type = "curve";
        });

        showGraphStats();

        // Show only neighbore nodes, edges and labes on click
        s.bind('clickNode', function(e) {
          var nodeId = e.data.node.id
          var that = this;
          this.node = e.data.node;
          
          if (mode == 0) {
            var toKeep = s.graph.neighbors(nodeId);
            toKeep[nodeId] = e.data.node;
            s.graph.nodes().forEach(function(n) {
              if (toKeep[n.id]) {
                n.color = n.originalColor;
                n.label = n.originalLabel;
              }
              else {
                n.color = '#eee';
                n.label = "";
              }
            });

            s.graph.edges().forEach(function(e) {
              if (toKeep[e.source] && toKeep[e.target])
                e.color = "rgba(180,180,180,0.5)";
              else
                e.color =  "rgba(180,180,180,0)";
            });
            s.settings({ labelThreshold : 2 });
            s.refresh();
          }

          $('#node_details')[0].innerHTML =
            '<label>ID: </label>' + this.node.id + '<br>' +
            '<label>Name: </label>' + this.node.label + '<br>' +
            '<label>Degree: </label>' + this.node.attributes.degree + '<br>' +
            '<label>Eccentricity: </label>' + this.node.attributes.eccentricity + '<br>' +
            '<label>Eigencentrality: </label>' + this.node.attributes.eigencentrality + '<br>' +
            '<label>Clustering: </label>' + this.node.attributes.clustering + '<br>' +
            '<label>Hub: </label>' + this.node.attributes.hub + '<br>' +
            '<label>Modularity Class: </label>' + this.node.attributes.modularity_class + '<br>'+
            '<label>Regression Slope: </label>' + this.node.attributes.slope + '<br>'+
            '<label>Regression Intercept: </label>' + this.node.attributes.intercept + '<br>'+
            '<label>Regression r2: </label>' + this.node.attributes.r2 + '<br>';
          // Get HistoData from Server for this node
          $.ajax({
            url: "/data/keyword/histogram/" + nodeId, 
            success: function(result) {
              $('#node_detail_trend')[0].innerHTML = "";
              var canvas = $('<canvas id="infochart" height="200" width="300"></canvas>').appendTo('#node_detail_trend');
              var ctx = canvas.get(0).getContext("2d");
              that.node.attributes.years = result.years;
              var barChartData = UTILS.prepareHistoData(that.node.attributes.years);
              var chart = new Chart(ctx).Bar(barChartData, {});
            }
          });
          $.ajax({
            url: "data/keyword/publications/" + nodeId,
            success: function(result) {
              // populate table
              $('#node_detail_pubs > tbody').empty();
              for (var r in result) {
                var res = result[r];
                $('#node_detail_pubs > tbody:last-child').append('<tr><td>'+
                  res.id + '</td><td>' + 
                  res.title + '</td><td>' + 
                  res.year + '</td><td>' + 
                  res.source + '</td></tr>');
              }
            }
          });
        });

        s.bind('doubleClickNode', function(e) {
          if (mode == 0) {
            var nodeId = e.data.node.id,
                toKeep = s.graph.neighbors(nodeId);
            toKeep[nodeId] = e.data.node;

            s.graph.nodes().forEach(function(n) {
              if (!toKeep[n.id]) {
                s.graph.dropNode(n.id);
              }
            });

            s.graph.edges().forEach(function(e) {
              e.color = "rgba(180,180,180,0.5)";
              if (!(toKeep[e.source] && toKeep[e.target])) {            
                s.graph.dropEdge(e.id)
              }
            });

            s.settings({ labelThreshold : 0 });
            s.refresh(); 
            startLayout();
            mode = 1;
          }  
        });

        // When the stage is clicked, we just color each
        // node and edge with its original color.
        s.bind('clickStage', function(e) {
          setDefaultGraph();

        });

        // Do intial stuff after the graph is loaded
        filter();

        loadTrends();
        loadNodeMesure('degree')
        s.settings({ labelThreshold : 4 });
        s.refresh();
      });
    };

    // Do aditional stuff after initializiing the graph
    loadInitalGraph();
  }
    

    // Wait for DOM the be ready before starting up this application   
    if (document.addEventListener) {
      document.addEventListener("DOMContentLoaded", init, false);
    } else {
      window.onload = init;
    }




/***********************************************************************
  Extensions to simga.js
  This might be moved to an extrenal file later on
************************************************************************/
var extend = function() {
  sigma.classes.graph.addMethod('neighbors', function(nodeId) {
    var k,
        neighbors = {},
        index = this.allNeighborsIndex[nodeId] || {};

    for (k in index)
      neighbors[k] = this.nodesIndex[k];

    return neighbors;
  });

  sigma.canvas.edges.curve = function(edge, source, target, context, settings) {
    var color = edge.color,
        prefix = settings('prefix') || '',
        edgeColor = settings('edgeColor'),
        defaultNodeColor = settings('defaultNodeColor'),
        defaultEdgeColor = settings('defaultEdgeColor'),
        controlPointX =
          (source[prefix + 'x'] + target[prefix + 'x']) / 2 +
          (target[prefix + 'y'] - source[prefix + 'y']) / 4,
        controlPointY =
          (source[prefix + 'y'] + target[prefix + 'y']) / 2 +
          (source[prefix + 'x'] - target[prefix + 'x']) / 4;

    if (!color)
      switch (edgeColor) {
        case 'source':
          color = source.color || defaultNodeColor;
          break;
        case 'target':
          color = target.color || defaultNodeColor;
          break;
        default:
          color = defaultEdgeColor;
          break;
      }

    context.strokeStyle = color;
    context.lineWidth = edge[prefix + 'size'];
    context.beginPath();
    context.moveTo(source[prefix + 'x'], source[prefix + 'y']);
    context.quadraticCurveTo(
      controlPointX,
      controlPointY,
      target[prefix + 'x'],
      target[prefix + 'y']
    );

    context.stroke();
    };
  }
}();

var ChartMethods = {
    // sort a dataset
    sort: function (chart, datasetIndex) {
        var data = []
        chart.datasets.forEach(function (dataset, i) {
            dataset.bars.forEach(function (bar, j) {
                if (i === 0) {
                    data.push({
                        label: chart.scale.xLabels[j],
                        values: [bar.value]
                    })
                } else 
                    data[j].values.push(bar.value)
            });
        })

        data.sort(function (a, b) {
            if (a.values[datasetIndex] > b.values[datasetIndex])
                return -1;
            else if (a.values[datasetIndex] < b.values[datasetIndex])
                return 1;
            else
                return 0;
        })

        chart.datasets.forEach(function (dataset, i) {
            dataset.bars.forEach(function (bar, j) {
                if (i === 0)
                    chart.scale.xLabels[j] = data[j].label;
                bar.label = data[j].label;
                bar.value = data[j].values[i];
            })
        });
        chart.update();
    },
    // reload data
    reload: function (chart, datasetIndex, labels, values) {
        var diff = chart.datasets[datasetIndex].bars.length - values.length;
        if (diff < 0) {
            for (var i = 0; i < -diff; i++)
                chart.addData([0], "");
        } else if (diff > 0) {
            for (var i = 0; i < diff; i++)
                chart.removeData();
        }

        chart.datasets[datasetIndex].bars.forEach(function (bar, i) {
            chart.scale.xLabels[i] = labels[i];
            bar.value = values[i];
        })
        chart.update();
    }
}