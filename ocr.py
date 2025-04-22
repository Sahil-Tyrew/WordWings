# ocr.py

from PIL import Image
import pytesseract

def do_ocr(file_path: str, poppler_path: str = None) -> str:
    """
    Given an image or PDF path, run OCR and return the extracted text.
    If poppler_path is provided, it'll be used for PDF conversion.
    """
    text = ""
    if file_path.lower().endswith('.pdf'):
        from pdf2image import convert_from_path
        pages = convert_from_path(file_path, dpi=300, poppler_path=poppler_path)
        for page in pages:
            # convert to grayscale for better accuracy
            page = page.convert('L')
            text += pytesseract.image_to_string(page, lang='eng') + "\n\n"
    else:
        img = Image.open(file_path)
        img = img.convert('L')
        text = pytesseract.image_to_string(img, lang='eng')
    return text
