// fork getUserMedia for multiple browser versions, for the future
// when more browsers support MediaRecorder

navigator.getUserMedia = ( navigator.getUserMedia ||
                       navigator.webkitGetUserMedia ||
                       navigator.mozGetUserMedia ||
                       navigator.msGetUserMedia);

// set up basic variables for app

var record = document.getElementById("record");
var stop = document.getElementById("stop");
var upload = document.getElementById("upload");

var canvas = document.getElementById('visualizer');

var soundClips = document.getElementById('input-audio');
var cards = document.querySelectorAll('.card');

// var transOn = document.getElementById('trans-on');
// var transOff = document.getElementById('trans-off');

var clipContainer;
var divRow;
var divCol1;
//var divCol2;

var mediaRecorder = null;
var mediaStreamSource = null;
var analyser = null;
// disable stop button while not recording
stop.disabled = true;
upload.disabled = true;

//get DPI
let dpi = window.devicePixelRatio;

// visualiser setup - create web audio api context and canvas
var audioCtx = new (window.AudioContext || webkitAudioContext)();
audioCtx.resume().then(() => {
 console.log('Playback resumed successfully');
});
var canvasCtx = canvas.getContext("2d");


function fix_dpi() {
    //Get CSS height. The + prefix casts it to an integer. The slice method gets rid of "px"
    let style_height = +getComputedStyle(canvas).getPropertyValue("height").slice(0, -2);
    //Get CSS width
    let style_width = +getComputedStyle(canvas).getPropertyValue("width").slice(0, -2);
    //Scale the canvas
    canvas.setAttribute('height', style_height * dpi);
    canvas.setAttribute('width', style_width * dpi);
}

fix_dpi();


// function createToggle() {

//   var divContainer = document.createElement('div');
//   divContainer.setAttribute('class', 'btn-group btn-group-toggle');
//   divContainer.setAttribute('data-toggle', 'buttons');

//   var onLabel = document.createElement('label');
//   onLabel.setAttribute('id', 'trans-on-label');
//   onLabel.setAttribute('class', 'btn btn-secondary active');
//   onLabel.setAttribute('style', 'width: 7.8rem;height: 3rem; text-align: center; padding-top:0.8rem');
//   onLabel.innerText = 'Translate On';

//   var offLabel = document.createElement('label');
//   offLabel.setAttribute('id', 'trans-off-label');
//   offLabel.setAttribute('class', 'btn btn-secondary active');
//   offLabel.setAttribute('style', 'width: 7.8rem;height: 3rem; text-align: center; padding-top:0.8rem');
//   offLabel.innerText = 'Translate Off';

//   var onInput = document.createElement('input');
//   onInput.setAttribute('type', 'radio');
//   onInput.setAttribute('id', 'trans-on');
//   onInput.setAttribute('autocomplete', 'off');
  
//   onInput.checked = true;
//   onLabel.disabled = false;
//   onLabel.style.background = 'rgb(12, 168, 12)';
//   offLabel.style.background = '#888888';
//   offLabel.disabled = true;

//   var offInput = document.createElement('input');
//   offInput.setAttribute('type', 'radio');
//   offInput.setAttribute('id', 'trans-off');
//   offInput.setAttribute('autocomplete', 'off');

//   onInput.change = function() {
//       console.log("on clicked");
//       onInput.checked = true;
//       offInput.checked = false;
//       console.log(onInput.checked);
//       console.log(offInput.checked);
//       onLabel.disabled = false;
//       onLabel.style.background = 'rgb(12, 168, 12)';
//       offLabel.style.background = '#888888';
//       offLabel.disabled = true;
//   }

//   offInput.change = function() {
//       console.log("off clicked");
//       onInput.checked = false;
//       offInput.checked = true;
//       console.log(onInput.checked);
//       console.log(offInput.checked);
//       onLabel.style.background = '#888888';
//       onLabel.disabled = true;
//       offLabel.disabled = false;
//       offLabel.style.background = 'rgb(168, 48, 12)';
//   }
  
//   onLabel.appendChild(onInput);
//   offLabel.appendChild(offInput);
//   divContainer.appendChild(onLabel);
//   divContainer.appendChild(offLabel);

//   return divContainer;
// }

var allClips;
var clipIndex;
var sentence;

//main block for doing the audio recording
if (navigator.getUserMedia) {
  console.log('getUserMedia supported.');

  var constraints = { audio: true };
  //var constraints = { audio: { sampleSize: 16, channelCount: 1, sampleRate: 16000 } };

  var snd = document.getElementById('audio-panel');
  if (snd != null){
    upload.disabled = false;
  }

  var chunks = [];

  var onSuccess = function(stream) {
    mediaRecorder = new MediaRecorder(stream);
    //mediaRecorder.mimeType = 'audio/wav';
    //mediaRecorder.audioChannels = 1;
    //mediaRecorder.audioBitsPerSecond = 256000;
    mediaStreamSource = audioCtx.createMediaStreamSource(stream);
    
    

    record.onclick = function() {
      for(var i = 0; i < cards.length; i++)
      {
        cards[i].style.visibility='hidden';
      }
      ////////////
      //var clipContainer = document.createElement('article');
      // divRow = document.createElement('div');
      // divRow.setAttribute('class', 'row');
      // divRow.setAttribute('id', 'audio-trans');
      //divRow.setAttribute('style', 'width: 100%; height:80px');
      
      // divCol1 = document.createElement('div');
      // divCol1.setAttribute('class', 'col-sm-8');
      // divCol1.setAttribute('id', 'audio-col');
      // divCol2 = document.createElement('div');
      // divCol2.setAttribute('class', 'col-sm-3');
      // divCol2.setAttribute('id', 'toggle-col');
      // divCol2.setAttribute('style', 'display: inline-block; padding-top: 1rem; ');

      //var toggleDiv  = createToggle();
      //divCol2.appendChild(toggleDiv);

      // divRow.appendChild(divCol1);
      //divRow.appendChild(divCol2);

      // clipContainer.appendChild(divRow);
      //clipContainer.appendChild(audio);
      
      //soundClips.innerHTML = '';
      //soundClips.appendChild(clipContainer);

      //divRow.style.visibility = 'hidden';


      visualize();
      startRecording();
      
    }

    stop.onclick = function() {
      mediaRecorder.stop();
      mediaStreamSource.disconnect();
      // console.log("Media Recorder State:")
      // console.log(mediaRecorder.state);
      // console.log("recorder stopped");
      record.style.background = "";
      record.style.color = ""; 
      record.disabled = false;
      upload.disabled = false;
      stop.disabled = true;
      
    }

    upload.onclick = function() {
      var spinnerDiv = document.getElementById('spinner-div');
      var spinner = document.createElement("div");
      spinner.setAttribute('class', "spinner-border");
      spinner.setAttribute('role', 'status');
      spinnerDiv.appendChild(spinner);


      upload.disabled = true;
      saveRecordings();
    }

    mediaRecorder.onstop = function(e) {
      // console.log("data available after MediaRecorder.stop() called.");

      var clipContainer = document.createElement('article');
      // var divRow = document.createElement('div');
      // divRow.setAttribute('class', 'row');
      // divRow.setAttribute('id', 'audio-trans');
      // divRow.setAttribute('style', 'width: 100%');
      
      // var divCol1 = document.createElement('div');
      // divCol1.setAttribute('class', 'col-sm-9');
      // divCol1.setAttribute('id', 'audio-col');
      // var divCol2 = document.createElement('div');
      // divCol2.setAttribute('class', 'col-sm-3');
      // divCol2.setAttribute('id', 'toggle-col');
      // divCol2.setAttribute('style', 'display: inline-block; padding-top: 1rem; ');

      var audio = document.createElement('audio');
      audio.setAttribute('id', 'audio-panel');
     
      clipContainer.classList.add('clip');
      audio.setAttribute('controls', '');
      //divCol1.appendChild(audio);

      //divRow.style.visibility = 'visible';

      // var toggleDiv  = createToggle();
      // divCol2.appendChild(toggleDiv);

      // divRow.appendChild(divCol1);
      // divRow.appendChild(divCol2);

      // clipContainer.appendChild(divRow);

      clipContainer.appendChild(audio);
      
      soundClips.innerHTML = '';
      soundClips.appendChild(clipContainer);

      audio.controls = true;
      var blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
      chunks = [];
      var audioURL = window.URL.createObjectURL(blob);
      audio.src = audioURL;
      // console.log("recorder stopped");

    }

    mediaRecorder.ondataavailable = function(e) {
      chunks.push(e.data);
    }
    // if (transOn != null){
    //   transOn.change = function() {
    //     console.log("on clicked");
    //     transOn.checked = true;
    //     transOff.checked = false;
    //     console.log(transOn.checked);
    //     console.log(transOff.checked);
    //     var onLabel = document.getElementById("trans-on-label");
    //     var offLabel = document.getElementById("trans-off-label");
    //     onLabel.disabled = false;
    //     onLabel.style.background = 'rgb(12, 168, 12)';
    //     offLabel.style.background = '#888888';
    //     offLabel.disabled = true;
    //   }
    // }
    
    // if (transOff != null){
    //   transOff.change = function() {
    //     console.log("off clicked");
    //     transOn.checked = false;
    //     transOff.checked = true;
    //     console.log(transOn.checked);
    //     console.log(transOff.checked);
    //     var onLabel = document.getElementById("trans-on-label");
    //     var offLabel = document.getElementById("trans-off-label");
    //     onLabel.style.background = '#888888';
    //     onLabel.disabled = true;
    //     offLabel.disabled = false;
    //     offLabel.style.background = 'rgb(168, 48, 12)';
    //   }

    // }
  
  }

  var onError = function(err) {
    console.log('The following error occured: ' + err);
    var errorDiv = document.getElementById('error-logs');
    var errorMsg = document.createElement('div');
    errorMsg.setAttribute('class', 'alert alert-danger');
    errorMsg.setAttribute('role', 'alert');
    errorMsg.innerText = "Your device does not have a microphone. Please connect a microphone and press ctrl+F5";
    errorDiv.appendChild(errorMsg);
  }

  navigator.getUserMedia(constraints, onSuccess, onError);
} else {
  var errorDiv = document.getElementById('error-logs');
  var errorMsg = document.createElement('div');
  errorMsg.setAttribute('class', 'alert alert-danger');
  errorMsg.setAttribute('role', 'alert');
  errorMsg.innerText = "Your device does not have a mic. Please connect a microphone and press ctrl+F5";
  errorDiv.appendChild(errorMsg);

  console.log('getUserMedia not supported on your browser!');
  console.log('Your device does not support the HTML5 API needed to record audio (this is a known problem on iOS)');  
}

 function visualize() {
  var analyser = audioCtx.createAnalyser();
  mediaStreamSource.disconnect();
  mediaStreamSource.connect(analyser);

  analyser.fftSize = 256;
  var bufferLength = analyser.frequencyBinCount;
  var dataArray = new Uint8Array(bufferLength);
  WIDTH = canvas.width;
  HEIGHT = canvas.height;
  canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);
  draw()

  function draw() {

    requestAnimationFrame(draw);
    analyser.getByteFrequencyData(dataArray);
    canvasCtx.fillStyle = 'rgb(233, 236, 239)';
    canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

    var barWidth = Math.ceil((WIDTH / bufferLength) * 2);
    var barHeight;
    var x = 0;

    for(var i = 0; i < bufferLength; i++) {
      barHeight = Math.ceil((dataArray[i]/2) * 1.1);
      canvasCtx.fillStyle = 'rgb(' + (barHeight/1.1) + ',60,123)';
      canvasCtx.fillRect(x, HEIGHT-barHeight/2, barWidth, barHeight);
      x += barWidth + 1;
    }

  }
}


function startRecording() {

  if (mediaRecorder.state == 'recording'){
    // console.log("Already Recording")
    return;
  }

  audioCtx.resume().then(() => {
  //  console.log('Playback resumed successfully');
  });
  
  mediaRecorder.start();
  // console.log("Media Recorder State:")
  // console.log(mediaRecorder.state);
  // console.log("recorder started");
  
  upload.disabled = true;
  stop.disabled = false;
  
  record.style.background = "red";
  setTimeout(endRecording, 60000);
}

function endRecording() {
  if (mediaRecorder.state == 'inactive') {
    // The user has already pressed stop.
    return;
  }
  mediaRecorder.stop();
  // console.log(mediaRecorder.state);
  // console.log("recorder stopped");
  record.style.background = "";
  record.style.color = "";

  upload.disabled = false;
  stop.disabled = true;
  record.disabled = false;
}



function saveRecordings() {
  mediaStreamSource.disconnect();
  allClips = document.querySelectorAll('.clip');
  uploadCip();
}

function uploadCip() {
  
  var clip = allClips[0];
  // console.log(clip)
  //var word = clip.querySelector('p').innerText;

  clip.style.display = 'True';

  var audioBlobUrl = clip.querySelector('audio').src;
  // console.log(audioBlobUrl);

  //var toggle = document.getElementById('trans-on');
  //var translateOn = toggle.checked;
  
  var xhr = new XMLHttpRequest();
  console.log(audioBlobUrl)
  xhr.open('GET', audioBlobUrl, true);
  xhr.responseType = 'blob';
  xhr.onload = function(e) {
    if (this.status == 200) {
      var blob = this.response;
      console.log(blob)
      var ajaxRequest = new XMLHttpRequest();
      //var uploadUrl = '/upload?word=' + word 
      var uploadUrl = '/upload'
      //var uploadUrl = '/upload?trans=' + translateOn 
      
      ajaxRequest.open('POST', uploadUrl, true);
      ajaxRequest.setRequestHeader('Content-Type', 'application/json');    
      
                  ajaxRequest.onreadystatechange = function() {
                        if (ajaxRequest.readyState == 4) {
                            if (ajaxRequest.status === 200) {
                                    allDone();
                            } 
                            else {
                              alert('Uploading failed with error code ' + ajaxRequest.status);
                            }
                        }
                  };
      ajaxRequest.send(blob);
    }
  };
  xhr.send();
}



function allDone() {

  //document.cookie = 'all_done=true; path=/';

  location.reload(true);
  Window.location.reload();
}
