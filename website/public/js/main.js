var APP = function() {
  $.ajax({
    url: "/data/get/basicdata", 
    success: function(result) {
        $('#basicdata > tbody:last-child').append('<tr><td>Number of publications</td><td>'+ result.pubCount+'</td></tr>');
        $('#basicdata > tbody:last-child').append('<tr><td>Number of journals involved</td><td>'+result.journalCount+'</td></tr>');
        $('#basicdata > tbody:last-child').append('<tr><td>Number of publications from journals</td><td>'+result.pubJournalCount+'</td></tr>');
        var jList = '';
        for (j in result.topJournals) {
          var item = result.topJournals[j];
          jList += '<li>' + item.name + ' (' + item.count + ')</li>'; 
        }
        $('#basicdata > tbody:last-child').append('<tr><td>Top 3 journals</td><td><ol>'+jList+'</ol></td></tr>');
        $('#basicdata > tbody:last-child').append('<tr><td>Number of conferences involved</td><td>'+result.confCount+'</td></tr>');
        $('#basicdata > tbody:last-child').append('<tr><td>Number of publications from conferences</td><td>'+result.pubConfCount+'</td></tr>');
        var cList = '';
        for (j in result.topConfs) {
          var item = result.topConfs[j];
          cList += '<li>' + item.name + ' (' + item.count + ')</li>'; 
        } 
        $('#basicdata > tbody:last-child').append('<tr><td>Top 3 conferences</td><td><ol>'+cList+'</ol></td></tr>');
        $('#basicdata > tbody:last-child').append('<tr><td>Number of normalized keywords</td><td>'+result.tagCount+'</td></tr>');
    }
  });
}();