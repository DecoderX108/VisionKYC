import easyocr
import logging
from utils import setup_logging

setup_logging()

# Loading the EasyOCR models takes several seconds, so keep one Reader per
# language set for the lifetime of the process instead of one per request.
_readers = {}


def get_reader(languages):
    key = tuple(languages)
    if key not in _readers:
        logging.info(f"Loading EasyOCR reader for {list(key)}...")
        _readers[key] = easyocr.Reader(list(key))
    return _readers[key]


def extract_text(image_path, confidence_threshold=0.3, languages=['en']):
    """
    Extracts and filters text from an image using OCR, based on a confidence threshold.

    Parameters:
    - image_path (str | np.ndarray): Path to the image file, or the image array.
    - confidence_threshold (float): Minimum confidence for text inclusion. Default is 0.3.
    - languages (list): OCR languages. Default is ['en'].

    Returns:
    - str: Filtered text separated by '|' if confidence is met, otherwise an empty string.
    """

    logging.info("Text Extraction Started...")
    try:
        reader = get_reader(languages)
        result = reader.readtext(image_path)
        filtered_text = "|"
        for text in result:
            bounding_box, recognized_text, confidence = text
            if confidence > confidence_threshold:
                filtered_text += recognized_text + "|"

        return filtered_text
    except Exception as e:
        print("An error occurred during text extraction:", e)
        logging.info(f"An error occurred during text extraction: {e}")
        return ""
