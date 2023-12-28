import fitz  # PyMuPDF
import io
import os
from PyPDF2 import PdfWriter, PdfReader
from pdf2image import convert_from_path
from image_utils import enhance_and_ocr_images

def open_pdf(pdf_path: str) -> fitz.Document:
    """
    Open a PDF file and return the document object.

    Args:
        pdf_path (str): The file path to the PDF document.

    Returns:
        fitz.Document: The document object for the opened PDF.
    """
    return fitz.open(pdf_path)

def extract_images_from_pdf(pdf_document: fitz.Document) -> list:
    """
    Extract images from a PDF document and save them as TIFF files.

    Args:
        pdf_document (fitz.Document): The document object of the PDF.

    Returns:
        list: A list of image objects extracted from the PDF.
    """
    images = convert_from_path(pdf_document)
    for i, image in enumerate(images):
        image.save(f'page{i}.tif', 'TIFF')
    return images

def process_pdf_for_ocr(pdf_path: str) -> list:
    """
    Processes a PDF for OCR and returns the OCR output for each page.

    Args:
        pdf_path (str): The file path to the PDF document.

    Returns:
        list: OCR output for each page of the PDF.
    """
    pdf_document = open_pdf(pdf_path)
    images = extract_images_from_pdf(pdf_path)
    return enhance_and_ocr_images(images)

def create_output_pdf(pdf_file: str, pages: list) -> str:
    """
    Creates an output PDF from the given pages and returns the file path of the output PDF.

    Args:
        pdf_file (str): The file path to the original PDF document.
        pages (list): A list of OCR-processed page contents.

    Returns:
        str: The file path to the generated output PDF.
    """
    output_pdf = PdfWriter()
    base_filename = os.path.splitext(os.path.basename(pdf_file))[0]
    directory_filename = os.path.dirname(os.path.realpath(pdf_file))
    output_path = os.path.join(directory_filename, f"{base_filename}_OCR.pdf")

    with open(output_path, "wb") as output_file:
        for page_content in pages:
            text_io = io.BytesIO(page_content)
            text_pdf = PdfReader(text_io)
            output_pdf.add_page(text_pdf.pages[0])
        output_pdf.write(output_file)

    return output_path

def process_and_redact_pdf(input_pdf_path: str) -> str:
    """
    Processes a PDF for OCR, creates an output PDF with OCR content, and returns the file path of the output PDF.

    Args:
        input_pdf_path (str): The file path to the input PDF document.

    Returns:
        str: The file path to the output PDF with OCR content.
    """
    # Process the PDF for OCR
    ocr_pages = process_pdf_for_ocr(input_pdf_path)
    # Create the output PDF with OCR content
    output_pdf_path = create_output_pdf(input_pdf_path, ocr_pages)
    return output_pdf_path

def redact_pdf_partial(input_pdf: str, output_pdf: str, words_to_redact: list, proportion: float) -> None:
    """
    Partially redacts words in a PDF based on a given proportion.

    Args:
        input_pdf (str): File path to the input PDF document.
        output_pdf (str): File path for saving the redacted PDF document.
        words_to_redact (list): List of words to redact in the PDF document.
        proportion (float): Proportion of the word's length to be redacted.

    Returns:
        None
    """
    doc = open_pdf(input_pdf)
    for page in doc:
        for word in words_to_redact:
            text_instances = page.search_for(word)
            for inst in text_instances:
                redact_width = inst.width * proportion
                redact_area = fitz.Rect(inst.x1 - redact_width, inst.y0, inst.x1*1.02, inst.y1)
                annot = page.add_redact_annot(redact_area)
                annot.set_colors(stroke=(1, 0, 0), fill=(0, 0, 0))
        page.apply_redactions()
    doc.save(output_pdf)