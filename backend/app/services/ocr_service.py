from PIL import Image, ImageEnhance, ImageFilter
import easyocr
import numpy as np


class OCRService:

    def __init__(self):
        print("Loading EasyOCR model...")

        self.reader = easyocr.Reader(
            ["en"],
            gpu=False
        )

        print("EasyOCR model loaded.")

    def preprocess_image(self, image_path: str):
        image = Image.open(image_path)

        # Convert to grayscale
        image = image.convert("L")

        # Upscale image
        width, height = image.size

        image = image.resize(
            (width * 2, height * 2),
            Image.Resampling.LANCZOS
        )

        # Improve contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.8)

        # Sharpen text
        image = image.filter(
            ImageFilter.SHARPEN
        )

        return image

    def extract_text(self, image_path: str):

        processed_image = self.preprocess_image(
            image_path
        )

        image_array = np.array(
            processed_image
        )

        results = self.reader.readtext(
            image_array,
            detail=1,
            paragraph=False
        )

        extracted_text = []

        for result in results:

            bounding_box, text, confidence = result

            # Ignore extremely low-confidence detections
            if confidence >= 0.25:
                extracted_text.append({
                    "text": text,
                    "confidence": round(
                        float(confidence),
                        3
                    )
                })

        return extracted_text


ocr_service = OCRService()