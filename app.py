import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
import io
import pandas as pd

app = Flask(__name__)
tracked_products = []  # To store product details

# Pre-trained ResNet50 model for fruit/vegetable classification
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(1, activation='sigmoid')(x)  # Binary classification (Fresh/Not Fresh)
fruit_freshness_model = Model(inputs=base_model.input, outputs=predictions)

# Compile the model
fruit_freshness_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Function to preprocess image for classification
def preprocess_image(image):
    image_resized = cv2.resize(image, (224, 224))  # Resize to match model input size
    image_array = img_to_array(image_resized)
    image_array = np.expand_dims(image_array, axis=0)  # Expand dimensions to match model input
    image_array /= 255.0  # Normalize pixel values
    return image_array

# Function to classify the uploaded image as fruit or vegetable and predict freshness
def classify_and_predict(image):
    # Example classification logic (replace this with your trained model logic)
    image_array = preprocess_image(image)
    
    # This should call your fruit/vegetable classification model, e.g.:
    # predictions = your_model.predict(image_array)
    # Use the model to get the label for the type of fruit or vegetable
    predicted_label = "Apple,Banana,Cucumber,Tomato"  # Placeholder - replace with actual model output
    
    # Predict freshness using the freshness model
    freshness_prediction = fruit_freshness_model.predict(image_array)
    freshness = 'Fresh' if freshness_prediction[0][0] > 0.5 else 'Not Fresh'
    
    return predicted_label, freshness

# Function to process the image and extract product details
def process_image(image):
    fruit_veg_label, freshness = classify_and_predict(image)

    # Return detected product information
    product_info = {
        'brand': 'Unknown',  # Detected fruit/veg type
        'expiry': 'N/A',  # Expiry is N/A for fresh produce
        'quantity': '1 unit',  # Quantity is 1 unit for simplicity
        'freshness': freshness,
        'count': 1
    }
    
    tracked_products.append(product_info)  # Store the product info in tracked_products
    return product_info

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product_data')
def product_data():
    return jsonify(tracked_products)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        file = request.files['image']
        image = Image.open(file.stream)
        image = np.array(image)

        # Process image to detect product details
        product_info = process_image(image)
        return jsonify(product_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_excel')
def download_excel():
    try:
        # Convert tracked products to DataFrame for Excel export
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
