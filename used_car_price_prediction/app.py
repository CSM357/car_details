import os
import json
import http.client
import subprocess  # Import subprocess to run test.py
from flask import Flask, request, jsonify, render_template
from license_plate_recognition import recognize_license_plate  

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_vehicle_info(license_plate):
    # Create a subprocess to run test.py with the license plate as an argument
    try:
        result = subprocess.run(
            ['python', 'test.py', license_plate],  # Run test.py with the license plate
            check=True,  # Raise an error if the command fails
            capture_output=True
        )
        return True  # Return true if the command is successful
    except subprocess.CalledProcessError as e:
        print(f"Error running test.py: {e.stderr.decode()}")  # Log the error
        return False

@app.route('/')
def index():
    return render_template('index.html')  # Render the main HTML page

@app.route('/recognize_lp', methods=['POST'])
def recognize_license_plate_endpoint():
    lp_image = request.files.get('lp_image')
    
    if lp_image:
        # Save the uploaded image
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], lp_image.filename)
        lp_image.save(image_path)

        # Recognize the license plate text
        license_plate_text = recognize_license_plate(image_path)

        if license_plate_text:
            # Run test.py to fetch vehicle information
            success = get_vehicle_info(license_plate_text)
            if success:
                # Load the vehicle information from the saved JSON file
                with open('vehicle_info.json') as json_file:
                    vehicle_info = json.load(json_file)
                return jsonify({
                    'status': True,
                    'license_plate': license_plate_text,
                    'vehicle_info': vehicle_info
                })
            else:
                return jsonify({'status': False, 'error': 'Failed to fetch vehicle information'}), 400
        else:
            return jsonify({'status': False, 'error': 'No license plate detected'}), 400
    else:
        return jsonify({'status': False, 'error': 'No license plate image uploaded'}), 400
    
@app.route('/get-vehicle-details',methods = ['GET'])
def getVeichleDetail():
    with open("vehicle_info.json",'r') as fs:
        data = fs.read()
    return jsonify({'status': True, 'success': data}), 200


if __name__ == '__main__':
    app.run(debug=True)  # Start the Flask application in debug mode


