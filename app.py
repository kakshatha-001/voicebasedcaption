from flask import Flask, request, jsonify
import base64
import cv2
import numpy as np
import torch
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer
from PIL import Image
from gtts import gTTS
import os

app = Flask(__name__)

# Load pre-trained model, feature extractor, and tokenizer
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Set generation parameters with updated num_beams
max_length = 30
num_beams = 10  # Change this value to control the beam search width
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    image_data = base64.b64decode(data['image'].split(',')[1])
    nparr = np.fromstring(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply histogram equalization to improve contrast
    enhanced_gray = cv2.equalizeHist(gray)

    # Convert to LAB color space
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Split the LAB image into channels
    l, a, b = cv2.split(lab_image)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    clahe_l = clahe.apply(l)

    # Merge the CLAHE-enhanced L channel with the original A and B channels
    enhanced_lab = cv2.merge((clahe_l, a, b))

    # Convert back to BGR color space
    enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # Convert from BGR format to RGB format
    pil_image = Image.fromarray(cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB))

    # Generate caption
    pixel_values = feature_extractor(images=[pil_image], return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    with torch.no_grad():
        output_ids = model.generate(pixel_values, **gen_kwargs)

    caption = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()

    # Convert caption to speech
    tts = gTTS(caption, lang='en')
    tts.save('static/caption.mp3')
    caption_audio_path = '/static/caption.mp3'

    return jsonify({'caption': caption, 'caption_audio_path': caption_audio_path})

if __name__ == '__main__':
    app.run(debug=True)
