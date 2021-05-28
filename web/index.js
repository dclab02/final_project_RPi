import "./index.css";

const file = document.getElementById("target");
const audio = document.getElementById("audio");

file.onchange = function () {
  const files = this.files;
  audio.src = URL.createObjectURL(files[0]);
  audio.load();
  audio.play();
  const context = new AudioContext();
  const src = context.createMediaElementSource(audio);
  const analyser = context.createAnalyser();
  const sampleRate = context.sampleRate;
  console.log(`SampleRate: ${sampleRate}`);

  const canvas = document.getElementById("canvas");
  canvas.width = 1200;
  canvas.height = 800;
  const ctx = canvas.getContext("2d");

  src.connect(analyser);
  analyser.connect(context.destination);

  analyser.fftSize = 16384;

  const bufferLength = analyser.frequencyBinCount;
  console.log(`bufferLength: ${bufferLength}`);

  const dataArray = new Uint8Array(bufferLength);

  const WIDTH = canvas.width;
  const HEIGHT = canvas.height;

  // log scale, target frequency
  // split to 64 bars
  const bars = 64;
  const scale = Math.pow(sampleRate / 2, 1 / bars);
  const targetFreqs = [];
  // start from freq 20 to sampleRate / 2
  for (let i = 20; i < sampleRate / 2; i *= scale) targetFreqs.push(i);
  console.log("targetFreqs", targetFreqs);
  const targetIndex = [];
  targetFreqs.forEach((freq) =>
    targetIndex.push(Math.round((freq / (sampleRate / 2)) * bufferLength))
  );
  console.log("targetIndex", targetIndex);

  function renderFrame() {
    requestAnimationFrame(renderFrame);
    analyser.getByteFrequencyData(dataArray);
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, WIDTH, HEIGHT);
    let barWidth = WIDTH / targetIndex.length;
    for (let i = 0, x = 0; i < targetIndex.length; ++i, x += barWidth + 1) {
      let barHeight = dataArray[targetIndex[i]];
      ctx.fillStyle = "#fff";
      ctx.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);
    }
  }

  audio.play();
  renderFrame();
};
