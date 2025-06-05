import os
import shutil
from fastapi import UploadFile
from typing import Union, IO
import PyPDF2
from docx import Document
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define a directory for uploads within the app structure or a configurable path
# For simplicity, let's assume a directory in the project root for now.
# Ensure this path is correctly handled in a production environment.
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_upload_file(upload_file: UploadFile, destination_folder: str = UPLOAD_DIR) -> str:
    """
    Saves an uploaded file to the specified folder.
    Returns the path to the saved file.
    """
    try:
        file_path = os.path.join(destination_folder, upload_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        logger.info(f"File '{upload_file.filename}' saved to '{file_path}'")
        return file_path
    except Exception as e:
        logger.error(f"Error saving file '{upload_file.filename}': {e}")
        raise
    finally:
        upload_file.file.close() # Ensure the file stream is closed

def extract_text_from_pdf(file_path: Union[str, IO[bytes]]) -> str:
    """
    Extracts text from a PDF file.
    Accepts either a file path or a file-like object.
    """
    text = ""
    try:
        if isinstance(file_path, str):
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text() or ""
        else: # Assuming file_path is a file-like object
            reader = PyPDF2.PdfReader(file_path)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() or ""
        logger.info(f"Text extracted successfully from PDF: {file_path if isinstance(file_path, str) else 'Uploaded File Stream'}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF '{file_path if isinstance(file_path, str) else 'Uploaded File Stream'}': {e}")
        # Depending on desired error handling, you might return empty string or raise
        return "" 

def extract_text_from_docx(file_path: Union[str, IO[bytes]]) -> str:
    """
    Extracts text from a DOCX file.
    Accepts either a file path or a file-like object.
    """
    text = ""
    try:
        doc = Document(file_path) # python-docx can handle both path string and file-like object
        for para in doc.paragraphs:
            text += para.text + "\n"
        logger.info(f"Text extracted successfully from DOCX: {file_path if isinstance(file_path, str) else 'Uploaded File Stream'}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX '{file_path if isinstance(file_path, str) else 'Uploaded File Stream'}': {e}")
        return ""

def get_text_from_file(file_path: str) -> str:
    """
    Detects file type and extracts text accordingly.
    """
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)
    elif extension == ".docx":
        return extract_text_from_docx(file_path)
    elif extension == ".txt":
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file '{file_path}': {e}")
            return ""
    else:
        logger.warning(f"Unsupported file type for text extraction: {extension} for file {file_path}")
        return "" # Or raise an error 