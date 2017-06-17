/* Presenting the geo data */
UTILS = {
  linearRegression : function(y,x){
    var lr = {};
    var n = y.length;
    var sum_x = 0;
    var sum_y = 0;
    var sum_xy = 0;
    var sum_xx = 0;
    var sum_yy = 0;
    
    for (var i = 0; i < y.length; i++) {
        
        sum_x += x[i];
        sum_y += y[i];
        sum_xy += (x[i]*y[i]);
        sum_xx += (x[i]*x[i]);
        sum_yy += (y[i]*y[i]);
    } 
    
    lr.slope = (n * sum_xy - sum_x * sum_y) / (n*sum_xx - sum_x * sum_x);
    lr.intercept = (sum_y - lr.slope * sum_x)/n;
    lr.r2 = Math.pow((n*sum_xy - sum_x*sum_y)/Math.sqrt((n*sum_xx-sum_x*sum_x)*(n*sum_yy-sum_y*sum_y)),2);
    return lr;
  },

  prepareHistoData : function(years) {
   var barChartData = {
        labels : [],
        datasets : [
            {
                fillColor : "rgba(151,187,205,0.5)",
                strokeColor : "rgba(151,187,205,0.8)",
                highlightFill : "rgba(151,187,205,0.75)",
                highlightStroke : "rgba(151,187,205,1)",
                data : []
            }
        ]
    }
    for (j=2005; j<2015; j++) {
        var found = false;
        for (y in years) {
            var sample = years[y];
                if (sample.year == j) {
                barChartData.labels.push(sample.year);
                barChartData.datasets[0].data.push(sample.count);
                found = true;
            }
        }
        if (!found) {
            barChartData.labels.push(j);
            barChartData.datasets[0].data.push(0);
        }
     }
    return barChartData;
  }
};