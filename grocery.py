import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
import pytesseract
import pandas as pd
import io
import re
from pytesseract import Output
import easyocr
from datetime import datetime

app = Flask(__name__)
tracked_products = []

# Predefined list of known brands
known_brands = ['Keo Karpin', 'Pond\'s', 'Dove', 'L\'Oreal', 'Nivea','Beardo','Sunflower Oil']

def filter_known_brand_names(text):
    for brand in known_brands:
        if re.search(brand, text, re.IGNORECASE):
            return brand
    return 'Unknown'

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    contrast_image = cv2.convertScaleAbs(gray, alpha=1.5, beta=50)

    edges = cv2.Canny(contrast_image, threshold1=50, threshold2=150)

    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    return dilated

def extract_text_with_tesseract(image):
    processed_image = preprocess_image(image)
    config = '--oem 3 --psm 6'  
    text = pytesseract.image_to_string(processed_image, config=config)
    return text

def extract_text_with_easyocr(image):
    reader = easyocr.Reader(['en'], gpu=False)  
    results = reader.readtext(image)
    text = " ".join([result[1] for result in results])
    return text

def extract_text(image):
    text = extract_text_with_tesseract(image)
    if not text.strip(): 
        text = extract_text_with_easyocr(image)
    return text

def extract_expiry_date(text):
    date_pattern = r'\b(0[1-9]|1[0-2])[/-](\d{4})\b|\b(0[1-9]|[12][0-9]|3[01])[/-](0[1-9]|1[0-2])[/-](\d{4})\b'
    match = re.search(date_pattern, text)
    return match.group(0) if match else 'Unknown'

def extract_quantity(text):
    quantity_pattern = r'(\d+(\.\d+)?\s?(ml|kg|g|l|oz|mg))'
    match = re.search(quantity_pattern, text, re.IGNORECASE)
    return match.group(0) if match else 'Unknown'

def estimate_freshness(expiry_date):
    try:
        expiry = datetime.strptime(expiry_date, '%d/%m/%Y') if '/' in expiry_date else datetime.strptime(expiry_date, '%m/%Y')
        days_left = (expiry - datetime.now()).days
        return 'Fresh' if days_left > 30 else 'Expiring Soon' if 0 < days_left <= 30 else 'Expired'
    except ValueError:
        return 'N/A'

# Function to process the image and extract product details
def process_image(image):
    text = extract_text(image)
    brand_name = filter_known_brand_names(text)
    expiry_date = extract_expiry_date(text)
    quantity = extract_quantity(text)
    freshness = estimate_freshness(expiry_date)

    product_info = {
        'brand': brand_name,
        'expiry': expiry_date,
        'quantity': quantity,
        'freshness': freshness,
        'count': 1
    }

    tracked_products.append(product_info)
    return product_info

# Flask routes for image upload
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        file = request.files['image']
        image = Image.open(file.stream)
        image = np.array(image)

        product_info = process_image(image)
        return jsonify(product_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/product_data')
def product_data():
    return jsonify(tracked_products)

@app.route('/download_excel')
def download_excel():
    try:
        df = pd.DataFrame(tracked_products)
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False)
        writer.close()
        output.seek(0)

        return send_file(output, download_name="detected_products.xlsx", as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
