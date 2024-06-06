// Function to preview the selected image
function previewImage(event) {
    const file = event.target.files[0];
    const image = document.getElementById('videoFeed');
    image.src = URL.createObjectURL(file);
    image.style.display = 'block';
}

// Function to capture image from video feed
function captureImage() {
    const video = document.getElementById('videoFeed');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg');
    const imageBlob = dataURItoBlob(imageData);
    const file = new File([imageBlob], 'image.jpg', { type: 'image/jpeg' });

    // Call function to generate caption
    generateCaption(file);
}

// Function to convert data URI to Blob
function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const intArray = new Uint8Array(arrayBuffer);
    for (let i = 0; i < byteString.length; i++) {
        intArray[i] = byteString.charCodeAt(i);
    }
    return new Blob([arrayBuffer], { type: mimeString });
}

// Function to generate caption from image
function generateCaption(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);

    fetch('/caption', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const caption = data.caption;
        displayCaption(caption);
        speakCaption(caption);
    })
    .catch(error => console.error('Error:', error));
}

// Function to display caption on the webpage
function displayCaption(caption) {
    const captionElement = document.getElementById('caption');
    captionElement.innerText = caption;
}

// Function to speak the caption
function speakCaption(caption) {
    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.src = `https://translate.google.com/translate_tts?ie=UTF-8&tl=en&q=${encodeURIComponent(caption)}`;
    audioPlayer.style.display = 'block';
    audioPlayer.play();
}
