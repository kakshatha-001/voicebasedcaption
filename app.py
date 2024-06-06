from flask import Flask, render_template, request, jsonify
import os
import cv2
import torch
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer
from PIL import Image
import numpy as np
from gtts import gTTS

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

def preprocess_image(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    if image is None:
        print(f"Warning: {image_path} does not exist or could not be loaded.")
        return None

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
    return pil_image

def predict_step(image_paths):
    images = []
    for image_path in image_paths:
        preprocessed_image = preprocess_image(image_path)
        if preprocessed_image:
            images.append(preprocessed_image)
        else:
            continue

    if not images:
        return []

    # Extract features and generate captions
    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    with torch.no_grad():
        output_ids = model.generate(pixel_values, **gen_kwargs)

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_caption', methods=['POST'])
def generate_caption():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Save the uploaded image
    image_path = 'uploads/' + file.filename
    file.save(image_path)

    # Generate caption
    predictions = predict_step([image_path])

    # Convert caption to speech
    caption = predictions[0]
    tts = gTTS(caption, lang='en')
    tts.save('static/caption.mp3')

    return jsonify({'caption': caption})

if __name__ == '__main__':
    app.run(debug=True)
