// Create WebSocket connection.
//const socket = new WebSocket('ws://' + window.location.host + ':8080');

var junoRequest;

$.ajax({
  url: "http://ip-api.com/json",
  type: 'GET',
  success: function(json)
  {
    junoRequest = '{'
                  +'"city":"' + json.city +'", '
                  +'"state":"' + json.regionName
                  + '}';
    console.log(junoRequest);
  },
  error: function(err)
  {
    console.log("Addressing failed, error= " + err);
  }
});