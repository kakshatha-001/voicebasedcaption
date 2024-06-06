import os
import cv2
import torch
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer
from PIL import Image
from gtts import gTTS
from flask import Flask, request, render_template, send_file
from io import BytesIO

app = Flask(__name__)

# Load pre-trained model, feature extractor, and tokenizer
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Set generation parameters with updated num_beams
max_length = 30
num_beams = 10
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Warning: {image_path} does not exist or could not be loaded.")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    enhanced_gray = cv2.equalizeHist(gray)
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab_image)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    clahe_l = clahe.apply(l)
    enhanced_lab = cv2.merge((clahe_l, a, b))
    enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
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

    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    with torch.no_grad():
        output_ids = model.generate(pixel_values, **gen_kwargs)

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            predictions = predict_step([file_path])
            if predictions:
                caption = predictions[0]
                tts = gTTS(caption, lang='en')
                tts.save('caption.mp3')
                return render_template('result.html', image_path=file_path, caption=caption)
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join('uploads', filename))

@app.route('/audio')
def get_audio():
    return send_file('caption.mp3', mimetype='audio/mp3')

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
