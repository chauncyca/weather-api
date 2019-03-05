// Create WebSocket connection.
//const socket = new WebSocket('ws://' + window.location.host + ':8080');

function retrieveWeather(obj) {
    
    const socket = new WebSocket('ws://127.0.0.1:8080');

    socket.onclose = function(e){ console.log("Socket connection closed"); };
    socket.onmessage = function(e){
                                        console.log("Socket message recieved", e.data);
                                        parseResponse(e.data);
                                  };
    socket.onerror = function(e) {console.log("Socket error", e.data);};

    var output = document.getElementById('output');
    var junoRequest;
    var dataToDisplay;

    getLocation();

    socket.onopen = ()=> socket.send(junoRequest)

    function parseResponse(response) {
        var jsonResponse = JSON.parse(response)
        console.log("Json response: ", jsonResponse);
        if(jsonResponse.action == "sendReq") {
            getWeatherFromApi();
        }
        else if (jsonResponse.action == "updatedCache"){
            console.log("Juno req: ", junoRequest);
            socket.send(junoRequest);
        }
        else if (jsonResponse.action == "failure") {
            console.log("Error cannot be handled, terminating.")
            socket.onclose = function () {}
            socket.close()
        }
        else if (jsonResponse){
            dataToDisplay = jsonResponse;
            output.innerHTML = response;
            console.log("Retrieved data. Closing socket.")
            socket.onclose = function () {}
            socket.close()
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
    }

    function getLocation(){
        $.ajax({
            url: "http://ip-api.com/json",
            type: 'GET',
            async: false,
            success: function(json)
            {
                junoRequest = '{"action":"retrieve",'
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
}

function getJSON(callback) {
    var xhr = new XMLHttpRequest(),
        method = 'GET';
    xhr.addEventListener('load', function (e) {
        callback(this.response);
    });
    xhr.open(method, "index.html");
    xhr.responseType = 'json';
    xhr.send();
}

window.addEventListener('load', function () {
    getJSON(retrieveWeather)
});


