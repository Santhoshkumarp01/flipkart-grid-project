# flipkart-grid-project
This project is a web-based application that uses Optical Character Recognition (OCR) and computer vision techniques to extract product details from images. The system is designed to recognize product brand names, expiry dates, and other attributes from images of product packaging, such as those found on Flipkart listings. It allows users to upload images of products, processes them to extract relevant information, and provides an option to download the data in Excel format.

Features
OCR-based Text Extraction: Uses Tesseract to extract text from product images.
Brand Name Detection: Recognizes known brand names from a predefined list.
Expiry Date Extraction: Identifies expiry dates using regular expressions.
Image Preprocessing: Enhances image quality for better OCR accuracy.
Data Storage: Keeps track of uploaded products with their extracted details.
Excel Export: Allows users to download product data in Excel format.

Tech Stack
Flask: Used for the web framework and serving the application.
Tesseract OCR: For extracting text from product images.
OpenCV: For preprocessing images (grayscale conversion, noise reduction, etc.).
NumPy: For numerical operations on images.
Pandas: For handling and exporting data as Excel files.
Regex: For pattern-based expiry date extraction.

Getting Started
Prerequisites
Before you begin, ensure you have met the following requirements:

Python 3.7 or higher installed on your machine
pip for installing dependencies
Installation
Clone the repository to your local machine:

bash
Copy code
git clone https://github.com/Santhoshp01/flipkart-grid-project.git

cd flipkart-product-classifier
Install the required dependencies:
bash
Copy code
pip install -r requirements.txt
The main dependencies include:

Flask
OpenCV
NumPy
Pandas
Pillow (for image handling)
Tesseract OCR
Install Tesseract OCR on your system:

Linux: Install via your package manager.
sudo apt install tesseract-ocr
Windows: Download and install from Tesseract official website.

Ensure Tesseract is added to your system's PATH.

(Optional) Install any pre-trained model for advanced text classification if needed.

Usage
Run the Flask application:
python app.py
Open your browser and navigate to http://127.0.0.1:5000/.

Upload a product image using the interface and see the extracted details such as the brand name and expiry date.

Download the processed product information in Excel format.

Example
Upload a product image.
The system processes the image and displays the extracted brand, expiry date, and other relevant data.
You can also export the data to an Excel file.

Folder Structure
flipkart-grid-project/
│
├── app.py                  # Main Flask application
├── static/                 # Static files (CSS, JS, etc.)
├── templates/              # HTML templates for the app
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation

API Endpoints
/upload (POST): Accepts image files for processing.
/product_data (GET): Returns a JSON object containing the processed product details.
/download_excel (GET): Allows users to download an Excel file with the extracted product information.
Contributing
If you want to contribute to this project, please follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes and commit them (git commit -m 'Add some feature').
Push to the branch (git push origin feature-branch).
Open a Pull Request.
License
This project is licensed under the MIT License. See the LICENSE file for more details.
