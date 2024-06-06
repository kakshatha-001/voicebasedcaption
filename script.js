function processImage() {
    var fileInput = document.getElementById('imageInput');
    var file = fileInput.files[0];
    var reader = new FileReader();
    
    reader.onload = function(e) {
        var image = new Image();
        image.src = e.target.result;
        image.onload = function() {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            canvas.width = this.width;
            canvas.height = this.height;
            ctx.drawImage(this, 0, 0);
            var dataUrl = canvas.toDataURL('image/jpeg');

            // Send dataUrl to server for processing and captioning
            fetch('/process_image', {
                method: 'POST',
                body: JSON.stringify({ image: dataUrl }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                var outputDiv = document.getElementById('output');
                outputDiv.innerHTML = data.caption;
            })
            .catch(error => console.error('Error:', error));
        }
    };
    reader.readAsDataURL(file);
}
