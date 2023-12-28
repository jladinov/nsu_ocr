import io
import re
import fitz
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from concurrent.futures import ThreadPoolExecutor
from utility_functions import append_to_json_file, extract_dates

def extract_images_from_page(page: fitz.Page) -> list:
    """
    Extracts images from a single PDF page.

    Args:
        page (fitz.Page): A page object from a PDF document.

    Returns:
        list: A list of PIL Image objects extracted from the PDF page.
    """
    images = []
    image_list = page.get_images(full=True)
    for img in enumerate(image_list, start=1):
        xref = img[0]
        base_image = page.parent.extract_image(xref)
        image_bytes = base_image["image"]
        images.append(Image.open(io.BytesIO(image_bytes)))
    return images

def enhance_image(image: Image.Image) -> Image.Image:
    """
    Applies enhancement techniques to a single image.

    Args:
        image (Image.Image): A PIL Image object to be enhanced.

    Returns:
        Image.Image: The enhanced image.
    """
    image = image.convert('L')  # Convert to grayscale
    image = image.resize(tuple(2 * x for x in image.size), Image.Resampling.LANCZOS)
    image = ImageEnhance.Contrast(image).enhance(2)  # Enhance contrast
    image = ImageEnhance.Brightness(image).enhance(2)  # Enhance brightness
    image = image.filter(ImageFilter.MedianFilter())
    image = apply_threshold(image)  # Apply thresholding
    orientation_data = pytesseract.image_to_osd(image)
    rotation_angle = int(re.search('Rotate: (\d+)', orientation_data).group(1))
    rotated_image = image.rotate(rotation_angle, expand=True)
    return rotated_image

def apply_threshold(image: Image.Image) -> Image.Image:
    """
    Apply a binary threshold to an image.

    Args:
        image (Image.Image): A PIL Image object.

    Returns:
        Image.Image: The threshold-applied image.
    """
    return image.point(lambda p: 255 if p > 128 else 0)

def perform_ocr_on_image(image: Image.Image) -> bytes:
    """
    Performs OCR on a single image and returns the extracted text as a PDF.

    Args:
        image (Image.Image): A PIL Image object to perform OCR on.

    Returns:
        bytes: The OCR output in PDF format.
    """
    config = '--psm 4 preserve_interword_spaces=1'
    OCR = pytesseract.image_to_string(image)
    DOB = extract_dates(OCR)
    if DOB: append_to_json_file('data\\uploads\\data.json', DOB)
    return pytesseract.image_to_pdf_or_hocr(image, config=config, extension='pdf')

def enhance_and_ocr_images(images: list) -> list:
    """
    Enhance images and perform OCR in parallel.

    Args:
        images (list): A list of PIL Image objects.

    Returns:
        list: A list of results from the OCR process.
    """
    with ThreadPoolExecutor() as executor:
        results = executor.map(enhance_and_ocr_single_image, images)
    return list(results)

def enhance_and_ocr_single_image(image: Image.Image) -> bytes:
    """
    Enhances a single image and performs OCR.

    Args:
        image (Image.Image): A PIL Image object.

    Returns:
        bytes: The OCR output in PDF format.
    """
    enhanced_image = enhance_image(image)
    return perform_ocr_on_image(enhanced_image)
