const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture-btn');
const startRecordingBtn = document.getElementById('start-recording-btn');
const stopRecordingBtn = document.getElementById('stop-recording-btn');
const captionElement = document.getElementById('caption');

let stream;
let recorder;
let chunks = [];

captureBtn.addEventListener('click', captureImage);
startRecordingBtn.addEventListener('click', startRecording);
stopRecordingBtn.addEventListener('click', stopRecording);

function captureImage() {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');
    sendData(imageData);
}

async function startRecording() {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => chunks.push(e.data);
    recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        sendData(audioBlob);
        chunks = [];
    };
    recorder.start();
    stopRecordingBtn.disabled = false;
}

function stopRecording() {
    recorder.stop();
    stopRecordingBtn.disabled = true;
    stream.getTracks().forEach(track => track.stop());
}

async function sendData(data) {
    const formData = new FormData();
    formData.append('data', data);

    const response = await fetch('/process', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    captionElement.innerText = result.caption;
}
