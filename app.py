import os
from flask import Flask, request, render_template, send_from_directory
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer
from PIL import Image
import torch
import cv2
from gtts import gTTS

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

max_length = 30
num_beams = 10
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
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
    images = [preprocess_image(path) for path in image_paths if preprocess_image(path) is not None]
    if not images:
        return []

    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    with torch.no_grad():
        output_ids = model.generate(pixel_values, **gen_kwargs)

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    return [pred.strip() for pred in preds]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            predictions = predict_step([filepath])
            if predictions:
                caption = predictions[0]
                tts = gTTS(caption, lang='en')
                tts.save(os.path.join(app.config['UPLOAD_FOLDER'], 'caption.mp3'))
                return render_template('index.html', image_url=filepath, caption=caption, audio_url='static/uploads/caption.mp3')
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
