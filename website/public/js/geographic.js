/*
    This Application displays the data collected from PLM publication in a geographic context
*/

var APP = function() {
    var that = this;
    var geojson;


    this.getColor = function(d) {
        return d > 500 ? '#800026' :
           d > 200  ? '#BD0026' :
           d > 150  ? '#E31A1C' :
           d > 100  ? '#FC4E2A' :
           d > 50   ? '#FD8D3C' :
           d > 20   ? '#FEB24C' :
           d > 10   ? '#FED976' :
                      '#FFEDA0';
    }

    this.style = function(feature) {
        return {
            fillColor: that.getColor(feature.properties.count),
            weight: 2,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
        };
    };

    this.highlightFeature = function(e) {
        var layer = e.target;

        layer.setStyle({
            weight: 3,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.7
        });

        if (!L.Browser.ie && !L.Browser.opera) {
            layer.bringToFront();
        }

        info.update(layer.feature.properties);
    };

    this.resetHighlight = function(e) {
        that.geojson.resetStyle(e.target);
        info.update();
    };

    this.showDetails = function (e) {
        
         $('html, body').animate({
            scrollTop: $("#anch_" + e.target.feature.properties.id).offset().top
        }, 1000);
    };

    this.info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };

    // method that we will use to update the control based on feature properties passed
    info.update = function (props) {
        this._div.innerHTML = '<h4>Country Details</h4>' +  (props ?
            '<b>' + props.name + '</b><br/>' + props.count + ' Publications</br><div id="infodetails"></div>'
            : 'Hover over a country');
        if (props) {
            var barChartData = that.prepareHistoData(props.years);            
            var canvas = $('<canvas id="infochart" height="200" width="300"></canvas>').appendTo('#infodetails')
            var ctx = canvas.get(0).getContext("2d");
            var chart = new Chart(ctx).Bar(barChartData, {
                //responsive : true
            });
        }
    };

    this.prepareHistoData = function(years) {
        return UTILS.prepareHistoData(years);
    }

    var map = L.map('map').setView([51.505, -0.09], 2);
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        id: 'mapbox.light',
        accessToken: 'pk.eyJ1IjoibnlmZWxpeCIsImEiOiJjaWowMGo0bGMwMDM1djJtNTAzdXRoeXVqIn0.vYMhmirhVzzcGSrhhFSUww'
    }).addTo(map);

    this.info.addTo(map);

    $.ajax({
        url: "/data/get/geojson/metadata?filter=all", 
        success: function(result){
            that.geojson = L.geoJson(result, {
                style: that.style,
                onEachFeature: function (feature, layer) {
                    // Add Event Handlers
                    layer.on({
                        mouseover: that.highlightFeature,
                        mouseout: that.resetHighlight,
                        click: that.showDetails
                    });
                    // Create Lables for Country
                    /*var label = L.marker(layer.getBounds().getCenter(), {
                      icon: L.divIcon({
                        className: 'label',
                        html: feature.properties.name + '<br>' + feature.properties.count,
                        iconSize: [100, 40]
                      })
                    }).addTo(map);*/
                    var barChartData = that.prepareHistoData(feature.properties.years);
                    /* $('#details').append('<h3 id="anch_' + feature.properties.id + '">' + feature.properties.name + '</h3>' +
                        '<p><a href="#header">back to map</p></a>'
                    ); 
                    var ctxid = 'canvas_' + feature.properties.id;
                    var canvas = $('<canvas id="' + ctxid + '" height="200" width="300"></canvas>').appendTo('#details')
                    var ctx = canvas.get(0).getContext("2d");
                    canvas.insertBefore();
                    var chart = new Chart(ctx).Bar(barChartData, {
                        //responsive : true
                    }); */
                }
            }).addTo(map);
        }
    });

    

}();