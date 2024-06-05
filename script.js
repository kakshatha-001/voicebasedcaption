const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture-btn');
const recordBtn = document.getElementById('record-btn');
const status = document.getElementById('status');
const captionContainer = document.getElementById('caption-container');
const captionText = document.getElementById('caption');

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error('Error accessing the camera', error);
    });

captureBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
        uploadImage(blob);
    }, 'image/jpeg');
});

recordBtn.addEventListener('click', () => {
    recordAudio();
});

function uploadImage(blob) {
    const formData = new FormData();
    formData.append('file', blob, 'image.jpg');

    fetch('https://colab.research.google.com/drive/1ta1M6AqSZrg38NNDjaPNefwgG7BlIajt?usp=sharing/upload_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        captionText.innerText = data.caption;
        status.innerText = "Caption generated successfully.";
    })
    .catch(error => {
        console.error('Error uploading image', error);
        status.innerText = "Failed to generate caption.";
    });
}

function recordAudio() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            status.innerText = "Recording...";

            mediaRecorder.ondataavailable = event => {
                const audioBlob = event.data;
                uploadAudio(audioBlob);
            };

            setTimeout(() => {
                mediaRecorder.stop();
                status.innerText = "Recording stopped.";
            }, 5000); // Record for 5 seconds
        })
        .catch(error => {
            console.error('Error accessing the microphone', error);
            status.innerText = "Failed to access microphone.";
        });
}

function uploadAudio(blob) {
    const formData = new FormData();
    formData.append('file', blob, 'audio.wav');

    fetch('https://colab.research.google.com/drive/1ta1M6AqSZrg38NNDjaPNefwgG7BlIajt?usp=sharing/upload_audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        captionText.innerText = data.caption;
        status.innerText = "Caption generated successfully.";
    })
    .catch(error => {
        console.error('Error uploading audio', error);
        status.innerText = "Failed to generate caption.";
    });
}
