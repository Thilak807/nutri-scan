# from PIL import Image
import pytesseract
import cv2
import os
import numpy as np
#pytesseract.pytesseract.tesseract_cmd = r"C:\Users\REENA\AppData\Local\Programs\Tesseract-OCR\Tesseract.exe"

class OCR:
    @staticmethod
    def apply_threshold(img, argument):
        # Applying blur (each of which has its pros and cons, however,
        # median blur and bilateral filter usually perform better than gaussian blur.):

        switcher = {
            "GaussianBlur": cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            "bilateralFilter": cv2.threshold(cv2.bilateralFilter(img, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            "medianBlur": cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            "GaussianBlurAdaptive": cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
            "bilateralFilterAdaptive": cv2.adaptiveThreshold(cv2.bilateralFilter(img, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
            "medianBlurAdaptive": cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
        }
        return switcher.get(argument, "Invalid method")

    def get_string_from_image(self, img_path: str, method: str):
        output_dir = "/home/rem/WORK/NutriScan/OCR/results"
        used_option = ""

        # Read image using opencv
        img = cv2.imread(img_path)
        # Extract the file name without the file extension
        file_name = str(os.path.basename(img_path).split('.')[0])  # Convert to string


        # Create a directory for outputs
        output_path = str(os.path.join(output_dir, file_name))
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        # Rescaling the image
        img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)

        # Converting image to gray-scale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Applying dilation and erosion to remove the noise
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)

        # Apply threshold to get image with only black and white
        img = self.apply_threshold(img, method)

        # Save the filtered image in the output directory
        save_path = str(os.path.join(output_path, file_name + "_filter_" + str(method) + used_option + ".jpg"))
        cv2.imwrite(save_path, img)

        # Recognize text with tesseract for python
        result = pytesseract.image_to_string(img, lang='eng')

        # write result to a file
        text_output_file_path = save_path[:-4] + ".txt"
        text_output_file = open(text_output_file_path, "w+", encoding="utf-8")
        text_output_file.write(result)
        text_output_file.close()

        return result, text_output_file_path  # Returning both recognized text and path of the generated text file

    # list_of_methods = ["GaussianBlur", "bilateralFilter", "medianBlur", "GaussianBlurAdaptive", "bilateralFilterAdaptive", "medianBlurAdaptive"]