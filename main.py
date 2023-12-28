import os
import json
import fitz  # PyMuPDF
from pdf_utils import process_and_redact_pdf, redact_pdf_partial


def execute_ocr(input_pdf_path: str) -> str:
    """
    Executes OCR on a given PDF and performs redaction based on extracted data.

    Args:
        input_pdf_path (str): File path to the input PDF document.

    Returns:
        str: File path to the output PDF after redaction, or the original file path if redaction fails.
    """
    file_path = 'data\\uploads\\data.json'
    if os.path.isfile(file_path): 
        os.remove(file_path)
    file_path = os.path.join("data\\uploads", 'data.json')

    if not os.path.isfile(file_path):
        with open(file_path, 'w') as file:
            file.write('')  # Create an empty file

    output_pdf_path = process_and_redact_pdf(input_pdf_path)

    if os.path.isfile(output_pdf_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            for sublist in data:
                for item in sublist:
                    date = item.get('date', 'No date')
                    age = item.get('age', 'No age')
                    year = item.get('year', 'No year')
                    proportion = len(str(year)) / len(str(date))
                    words_to_redact = [date]
                    dir_name, file_name = os.path.split(output_pdf_path)
                    base_name, ext = os.path.splitext(file_name)
                    redacted_file_path = os.path.join(dir_name, base_name + '_redacted' + ext)
                    redact_pdf_partial(output_pdf_path, redacted_file_path, words_to_redact, proportion)
        except ValueError as e:
            return output_pdf_path
        return redacted_file_path

