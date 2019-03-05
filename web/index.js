// Create WebSocket connection.
//const socket = new WebSocket('ws://' + window.location.host + ':8080');
const socket = new WebSocket('ws://127.0.0.1:8080');
console.log("Listening")

socket.onclose = function(e){ console.log("Socket connection closed"); };
socket.onmessage = function(e){
                                    console.log("Socket message recieved", e.data);
                                    parseResponse(e.data);
                              };
socket.onerror = function(e) {console.log("Socket error", e.data);};

var junoRequest;
junoRequest = getLocation();

socket.onopen = ()=> socket.send(junoRequest)

function parseResponse(response) {
    var jsonResponse = JSON.parse(response)
    console.log("Json response: ", jsonResponse);
    if(jsonResponse.action == "sendReq") {
        getWeatherFromApi();
    }
    else if (jsonResponse.action == "updatedCache"){
        junoRequest = getLocation();
        console.log("Juno req: ", junoRequest);
        socket.send(junoRequest);
    }
    else {
        console.log("Bad response: ", response);
    }
}

function getWeatherFromApi() {
    const Http = new XMLHttpRequest();
    const url =  "https://j9l4zglte4.execute-api.us-east-1.amazonaws.com/api/ctl/weather/"
    Http.open("GET", url);
    Http.send();
    
    Http.onreadystatechange=(e)=> {
        socket.send(Http.responseText)
    }
//    $.ajax({
//        url: "https://j9l4zglte4.execute-api.us-east-1.amazonaws.com/api/ctl/weather/",
//        type: 'GET',
//        success: function(json)
//        {
//            console.log(json.)
//            socket.send(json)
//        },
//        error: function(err)
//        {
//            console.log("Failed to aquire weather data, error= " + err);
//        }
//    });
}

function getLocation(){
    $.ajax({
    url: "http://ip-api.com/json",
    type: 'GET',
    success: function(json)
    {
        return '{"action":"retrieve",'
                  +'"city":"' + json.city +'", '
                  +'"state":"' + json.regionName + '"'
                  + '}';
    },
    error: function(err)
    {
        console.log("Addressing failed, error= " + err);
    }
});
}

