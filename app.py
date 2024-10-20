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
tracked_products = [] 

base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(1, activation='sigmoid')(x) 
fruit_freshness_model = Model(inputs=base_model.input, outputs=predictions)


fruit_freshness_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

def preprocess_image(image):
    image_resized = cv2.resize(image, (224, 224)) 
    image_array = img_to_array(image_resized)
    image_array = np.expand_dims(image_array, axis=0) 
    image_array /= 255.0 
    return image_array

def classify_and_predict(image):
    image_array = preprocess_image(image)
    
    
    predicted_label = "Apple,Banana,Cucumber,Tomato" 
    freshness_prediction = fruit_freshness_model.predict(image_array)
    freshness = 'Fresh' if freshness_prediction[0][0] > 0.5 else 'Not Fresh'
    
    return predicted_label, freshness

def process_image(image):
    fruit_veg_label, freshness = classify_and_predict(image)

    product_info = {
        'brand': 'Unknown',  
        'expiry': 'N/A',  
        'quantity': '1 unit', 
        'freshness': freshness,
        'count': 1
    }
    
    tracked_products.append(product_info)  
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

        product_info = process_image(image)
        return jsonify(product_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
