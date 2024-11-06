import cv2
import pytesseract
import numpy as np
import re

def recognize_license_plate(image_path):
    try:
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print("Error: Image not found or unable to load.")
            return None

        # Convert to grayscale and apply filters
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        # Increase contrast and apply sharpening to enhance edges
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(gray, -1, kernel)

        # Edge detection and contour finding
        edged = cv2.Canny(sharpened, 30, 200)  # You can try increasing/decreasing these thresholds
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours based on area, looking for a rectangular one
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]  # Consider more contours
        screenCnt = None

        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.018 * peri, True)
            if len(approx) == 4:  # Looking for a quadrilateral (license plate)
                screenCnt = approx
                break

        if screenCnt is None:
            print("No license plate detected")
            return None

        # Mask the license plate area
        mask = np.zeros(gray.shape, dtype=np.uint8)
        masked = cv2.drawContours(mask, [screenCnt], -1, 255, -1)
        masked = cv2.bitwise_and(image, image, mask=mask)

        # Extract the license plate region
        x, y, w, h = cv2.boundingRect(screenCnt)
        # Expand the ROI slightly to increase detection area
        padding = 10  # You can adjust the padding value
        x, y, w, h = max(0, x - padding), max(0, y - padding), w + 2 * padding, h + 2 * padding
        license_plate = gray[y:y+h, x:x+w]

        # Resize for better OCR accuracy and apply binary threshold
        license_plate = cv2.resize(license_plate, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        _, license_plate = cv2.threshold(license_plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Use Tesseract with a configuration optimized for alphanumeric text
        config = '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = pytesseract.image_to_string(license_plate, config=config)

        # Clean and validate detected text
        cleaned_text = re.sub(r'[^A-Z0-9]', '', text).strip()

        # Apply post-processing to fix common character misreads
        corrected_text = cleaned_text.replace('1Z', '12').replace('O', '0').replace('I', '1').replace('B', '8')

        # Validate using a regex for license plate formats
        if re.match(r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$', corrected_text):
            return corrected_text
        else:
            print("Warning: Detected text may be incorrect")
            return corrected_text

    except Exception as e:
        print(f"Error in recognize_license_plate: {e}")
        return None