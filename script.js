// Capture Image from Camera
const video = document.getElementById('video');
const captureBtn = document.getElementById('capture-btn');
const canvas = document.createElement('canvas');

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error('Error accessing camera: ', err);
    });

captureBtn.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');
    sendImageToColab(imageData);
});

// Record Voice from Microphone
const recordBtn = document.getElementById('record-btn');
const audio = document.getElementById('audio');
let mediaRecorder;
let audioChunks = [];

recordBtn.addEventListener('click', () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audio.src = URL.createObjectURL(audioBlob);
                sendAudioToColab(audioBlob);
                audioChunks = [];
            };

            setTimeout(() => {
                mediaRecorder.stop();
            }, 5000); // Record for 5 seconds
        })
        .catch(err => {
            console.error('Error accessing microphone: ', err);
        });
});

// Send Image to Colab
function sendImageToColab(imageData) {
    fetch('https://colab.research.google.com/drive/1ta1M6AqSZrg38NNDjaPNefwgG7BlIajt?usp=sharing/image', {
        method: 'POST',
        body: JSON.stringify({ image: imageData }),
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('caption').innerText = data.caption;
        speakCaption(data.caption);
    })
    .catch(err => {
        console.error('Error sending image to Colab: ', err);
    });
}

// Send Audio to Colab
function sendAudioToColab(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);

    fetch('https://colab.research.google.com/drive/1ta1M6AqSZrg38NNDjaPNefwgG7BlIajt?usp=sharing/audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('caption').innerText = data.caption;
        speakCaption(data.caption);
    })
    .catch(err => {
        console.error('Error sending audio to Colab: ', err);
    });
}

// Speak Caption
function speakCaption(caption) {
    const utterance = new SpeechSynthesisUtterance(caption);
    window.speechSynthesis.speak(utterance);
}
