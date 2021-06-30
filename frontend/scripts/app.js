let heading = document.querySelector('h1');
heading.textContent = 'Equalizer';
// heading.textContent = 'CLICK ANYWHERE TO START'
// document.body.addEventListener('click', init);

// parameters 
var pixelsPerDb;
var dbScale = 15;
var buffersize = 200;
var drawVisual;
var data = new Uint8Array(buffersize);
var parameterflag = false;
var mysocket = new WebSocket('ws://localhost:8765');
var datacount = 0;

// filter properties
var BF1_type = document.getElementById('BiquadFilter1_Type').value;
var BF1_f = parseFloat(document.getElementById("BiquadFilter1_frequency").value);
var BF1_g = parseFloat(document.getElementById("BiquadFilter1_Gain").value);
var BF1_q = parseFloat(document.getElementById("BiquadFilter1_Q").value);

var BF2_type = document.getElementById('BiquadFilter2_Type').value;
var BF2_f = parseFloat(document.getElementById("BiquadFilter2_frequency").value);
var BF2_g = parseFloat(document.getElementById("BiquadFilter2_Gain").value);
var BF2_q = parseFloat(document.getElementById("BiquadFilter2_Q").value);

var BF3_type = document.getElementById('BiquadFilter3_Type').value;
var BF3_f = parseFloat(document.getElementById("BiquadFilter3_frequency").value);
var BF3_g = parseFloat(document.getElementById("BiquadFilter3_Gain").value);
var BF3_q = parseFloat(document.getElementById("BiquadFilter3_Q").value);

var BF4_type = document.getElementById('BiquadFilter4_Type').value;
var BF4_f = parseFloat(document.getElementById("BiquadFilter4_frequency").value);
var BF4_g = parseFloat(document.getElementById("BiquadFilter4_Gain").value);
var BF4_q = parseFloat(document.getElementById("BiquadFilter4_Q").value);

var BF5_type = document.getElementById('BiquadFilter5_Type').value;
var BF5_f = parseFloat(document.getElementById("BiquadFilter5_frequency").value);
var BF5_g = parseFloat(document.getElementById("BiquadFilter5_Gain").value);
var BF5_q = parseFloat(document.getElementById("BiquadFilter5_Q").value);


// init
init();

function init() {
    // websocket
    mysocket.onopen = function(event) {
        console.log('WebSocket is connected.');
      };

    mysocket.onmessage = function(e) {
        if (e.data === 'done'){
            datacount = 0;
            visualize();
        }
        else if (e.data === 'sendparameter_ack') {
              var json_data = {
                  "filters" :[
                      {
                          "type" : BF1_type,
                          "f" : BF1_f,
                          "g" : BF1_g,
                          "q" : BF1_q
                      },
                      {
                          "type" : BF2_type,
                          "f" : BF2_f,
                          "g" : BF2_g,
                          "q" : BF2_q
                      },
                      {
                          "type" : BF3_type,
                          "f" : BF3_f,
                          "g" : BF3_g,
                          "q" : BF3_q
                      },
                      {
                          "type" : BF4_type,
                          "f" : BF4_f,
                          "g" : BF4_g,
                          "q" : BF4_q
                      },
                      {
                          "type" : BF5_type,
                          "f" : BF5_f,
                          "g" : BF5_g,
                          "q" : BF5_q
                      }
                  ]
              };
              mysocket.send(JSON.stringify(json_data));
              parameterflag = false;
    
        }
        else {
            data[datacount] = parseInt(e.data);
            datacount += 1;
        }  
    };

    // set up audioCtx and filters
    var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    var BiquadFilter1 = audioCtx.createBiquadFilter();
    var BiquadFilter2 = audioCtx.createBiquadFilter();
    var BiquadFilter3 = audioCtx.createBiquadFilter();
    var BiquadFilter4 = audioCtx.createBiquadFilter();
    var BiquadFilter5 = audioCtx.createBiquadFilter();

    // set up canvas context for visualizer
    var canvas = document.querySelector('.visualizer');
    var canvasCtx = canvas.getContext("2d");
    var canvas_fr = document.querySelector('.visualizer_fr');
    var canvasCtx_fr = canvas_fr.getContext("2d");
    var intendedWidth = document.querySelector('.wrapper').clientWidth;
    canvas.setAttribute('width', intendedWidth);
    canvas_fr.setAttribute('width', intendedWidth);
    voiceChange();
    visualize();
    DrawFrequencyResponse();

    setInterval(function(){ 
        if (!parameterflag){
            mysocket.send("request"); 
        }}, 100);
    
    function visualize() {
        // console.log(data)
        WIDTH = canvas.width;
        HEIGHT = canvas.height;
        var bufferLengthAlt = data.length;
        var dataArrayAlt = data;
        canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);
        var drawAlt = function () {
            drawVisual = requestAnimationFrame(drawAlt);
            canvasCtx.fillStyle = 'rgb(0, 0, 0)';
            canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
            var barWidth = (WIDTH / bufferLengthAlt);
            var barHeight;
            var x = 0;

            for (var i = 0; i < bufferLengthAlt; i++) {
                barHeight = dataArrayAlt[i];
                canvasCtx.fillStyle = 'rgb(' + (barHeight + 100) + ',50,50)';
                canvasCtx.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);
                x += barWidth + 1;
            }
        };

        drawAlt();

    }

    function dbToY(db) {
        WIDTH = canvas.width;
        HEIGHT = canvas.height;
        var y = (0.5 * HEIGHT) - pixelsPerDb * db;
        return y;
    }
    
    function DrawFrequencyResponse() {
        // draw center
        var width = canvas_fr.width;
        var height = canvas_fr.height;
        canvasCtx_fr.fillStyle = "rgb(0, 0, 0)";
        canvasCtx_fr.fillRect(0, 0, width, height);
        
        canvasCtx_fr.strokeStyle = '"rgb(100,100,100)"';
        canvasCtx_fr.lineWidth = 3;
    
        canvasCtx_fr.beginPath();
        canvasCtx_fr.moveTo(0, 0);
    
        pixelsPerDb = (0.5 * height) / dbScale;
    
        var noctaves = 11;
    
        var frequencyHz = new Float32Array(width);
        var magResponse1 = new Float32Array(width);
        var phaseResponse1 = new Float32Array(width);
        var magResponse2 = new Float32Array(width);
        var phaseResponse2 = new Float32Array(width);
        var magResponse3 = new Float32Array(width);
        var phaseResponse3 = new Float32Array(width);
        var magResponse4 = new Float32Array(width);
        var phaseResponse4 = new Float32Array(width);
        var magResponse5 = new Float32Array(width);
        var phaseResponse5 = new Float32Array(width);
    
        var nyquist = 0.5 * audioCtx.sampleRate;
        // First get response.
        for (var i = 0; i < width; ++i) {
            var f = i / width;
    
            // Convert to log frequency scale (octaves).
            f = nyquist * Math.pow(2.0, noctaves * (f - 1.0));
    
            frequencyHz[i] = f;
        }
    
        BiquadFilter1.getFrequencyResponse(frequencyHz, magResponse1, phaseResponse1);
        BiquadFilter2.getFrequencyResponse(frequencyHz, magResponse2, phaseResponse2);
        BiquadFilter3.getFrequencyResponse(frequencyHz, magResponse3, phaseResponse3);
        BiquadFilter4.getFrequencyResponse(frequencyHz, magResponse4, phaseResponse4);
        BiquadFilter5.getFrequencyResponse(frequencyHz, magResponse5, phaseResponse5);

        canvasCtx_fr.strokeStyle = "rgb(224,27,106)";
        for (var i = 0; i < width; ++i) {
            // var f = magResponse2[i];
            var response = magResponse1[i] * magResponse2[i] * magResponse3[i] * magResponse4[i] *magResponse5[i];
            
            var dbResponse = 20.0 * Math.log(response) / Math.LN10;
            // dbResponse *= 2; // simulate two chained Biquads (for 4-pole lowpass)
            // console.log(dbResponse)
            var x = i;
            var y = dbToY(dbResponse);
            
            if (i === 0) {
                canvasCtx_fr.moveTo(x, y);
            }
            canvasCtx_fr.lineTo(x, y);
        }
        canvasCtx_fr.stroke();
    
        canvasCtx_fr.beginPath();
    
        canvasCtx_fr.lineWidth = 1;
    
        canvasCtx_fr.strokeStyle = "rgb(100,100,100)";
        // Draw frequency scale.
        for (var octave = 0; octave <= noctaves; octave++) {
            var x = octave * width / noctaves;
    
            canvasCtx_fr.strokeStyle = "rgb(100,100,100)";
            canvasCtx_fr.moveTo(x, 30);
            canvasCtx_fr.lineTo(x, height);
            canvasCtx_fr.stroke();
    
            var f = nyquist * Math.pow(2.0, octave - noctaves);
            canvasCtx_fr.textAlign = "center";
            canvasCtx_fr.strokeStyle = "rgb(224,27,106)";
            canvasCtx_fr.strokeText(f.toFixed(0) + "Hz", x, 20);
        }
    
        // Draw 0dB line.
        canvasCtx_fr.beginPath();
        canvasCtx_fr.moveTo(0, 0.5 * height);
        canvasCtx_fr.lineTo(width, 0.5 * height);
        canvasCtx_fr.stroke();
    
        // Draw decibel scale.
        for (var db = -dbScale; db < dbScale; db += 10) {
            var y = dbToY(db);
            canvasCtx_fr.strokeStyle = "rgb(224,27,106)";
            canvasCtx_fr.strokeText(db.toFixed(0) + "dB", width - 40, y);
            canvasCtx_fr.strokeStyle = "rgb(100,100,100)";
            canvasCtx_fr.beginPath();
            canvasCtx_fr.moveTo(0, y);
            canvasCtx_fr.lineTo(width, y);
            canvasCtx_fr.stroke();
        }
    }

    function voiceChange() {
        BiquadFilter1.gain.value = 1;
        BiquadFilter2.gain.value = 1;
        BiquadFilter3.gain.value = 1;
        BiquadFilter4.gain.value = 1;
        BiquadFilter5.gain.value = 1;
        
        BF1_type = document.getElementById('BiquadFilter1_Type').value;
        BF1_f = parseFloat(document.getElementById("BiquadFilter1_frequency").value);
        BF1_g = parseFloat(document.getElementById("BiquadFilter1_Gain").value);
        BF1_q = parseFloat(document.getElementById("BiquadFilter1_Q").value);
    
        BF2_type = document.getElementById('BiquadFilter2_Type').value;
        BF2_f = parseFloat(document.getElementById("BiquadFilter2_frequency").value);
        BF2_g = parseFloat(document.getElementById("BiquadFilter2_Gain").value);
        BF2_q = parseFloat(document.getElementById("BiquadFilter2_Q").value);
    
        BF3_type = document.getElementById('BiquadFilter3_Type').value;
        BF3_f = parseFloat(document.getElementById("BiquadFilter3_frequency").value);
        BF3_g = parseFloat(document.getElementById("BiquadFilter3_Gain").value);
        BF3_q = parseFloat(document.getElementById("BiquadFilter3_Q").value);
    
        BF4_type = document.getElementById('BiquadFilter4_Type').value;
        BF4_f = parseFloat(document.getElementById("BiquadFilter4_frequency").value);
        BF4_g = parseFloat(document.getElementById("BiquadFilter4_Gain").value);
        BF4_q = parseFloat(document.getElementById("BiquadFilter4_Q").value);
    
        BF5_type = document.getElementById('BiquadFilter5_Type').value;
        BF5_f = parseFloat(document.getElementById("BiquadFilter5_frequency").value);
        BF5_g = parseFloat(document.getElementById("BiquadFilter5_Gain").value);
        BF5_q = parseFloat(document.getElementById("BiquadFilter5_Q").value);

        BiquadFilter1.type = BF1_type;
        BiquadFilter1.frequency.value = BF1_f;
        BiquadFilter1.gain.value = BF1_g;
        BiquadFilter1.Q.value = BF1_q;

        BiquadFilter2.type = BF2_type;
        BiquadFilter2.frequency.value = BF2_f;
        BiquadFilter2.gain.value = BF2_g;
        BiquadFilter2.Q.value = BF2_q;

        BiquadFilter3.type = BF3_type;
        BiquadFilter3.frequency.value = BF3_f;
        BiquadFilter3.gain.value = BF3_g;
        BiquadFilter3.Q.value = BF3_q;

        BiquadFilter4.type = BF4_type;
        BiquadFilter4.frequency.value = BF4_f;
        BiquadFilter4.gain.value = BF4_g;
        BiquadFilter4.Q.value = BF4_q;

        BiquadFilter5.type = BF5_type;
        BiquadFilter5.frequency.value = BF5_f;
        BiquadFilter5.gain.value = BF5_g;
        BiquadFilter5.Q.value = BF5_q;
        
    }
    // event listeners to change eq settings
    document.getElementById('confirm').onclick = function () {
    window.cancelAnimationFrame(drawVisual);
    voiceChange();
    parameterflag = true;
    mysocket.send("parameter");
    visualize();
    DrawFrequencyResponse();
    };

};

