function uploadImage() {
    var input = document.getElementById('imageInput');
    var file = input.files[0];

    if (file) {
        var formData = new FormData();
        formData.append('image', file);

        fetch('/generate_caption', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            displayImage(file);
            displayCaption(data.caption);
        })
        .catch(error => console.error('Error:', error));
    }
}

function displayImage(file) {
    var container = document.getElementById('imageContainer');
    container.innerHTML = '';
    var img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    container.appendChild(img);
}

function displayCaption(caption) {
    var captionElement = document.getElementById('caption');
    captionElement.textContent = caption;

    var audioElement = document.getElementById('audioCaption');
    audioElement.src = '/static/caption.mp3';
}
