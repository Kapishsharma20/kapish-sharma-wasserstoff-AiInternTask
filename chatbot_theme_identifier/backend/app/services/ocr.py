import os
import cv2
import numpy as np
import hashlib
import pytesseract
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text
from app.core.celery import celery
from app.core.database import database
from app.models.document import Document
from app.config import settings

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

def generate_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def is_searchable_pdf(file_path: str) -> bool:
    text = extract_text(file_path)
    return len(text.strip()) > 0

def get_ocr_confidence(img) -> float:
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    confidences = [float(c) for c in data['conf'] if c != '-1']
    return round(sum(confidences)/len(confidences), 2) if confidences else 0

def process_image(file_path: str) -> tuple[str, float]:
    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 6')
    return text, get_ocr_confidence(gray)

def process_pdf(file_path: str) -> tuple[str, float]:
    if is_searchable_pdf(file_path):
        text = extract_text(file_path)
        return text, 100.0  # Assume perfect confidence for searchable PDFs
    
    images = convert_from_path(
        file_path,
        dpi=settings.PDF_DENSITY,
        poppler_path=settings.POPPLER_PATH
    )
    
    full_text = ""
    total_confidence = 0.0
    for pil_img in images:
        img_array = np.array(pil_img.convert('RGB'))
        img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        page_text = pytesseract.image_to_string(gray, config='--psm 6')
        full_text += page_text + "\n"
        total_confidence += get_ocr_confidence(gray)
    
    avg_confidence = round(total_confidence / len(images), 2) if images else 0
    return full_text, avg_confidence

@celery.task
async def process_document(file_path: str):
    try:
        if file_path.lower().endswith('.pdf'):
            text, confidence = process_pdf(file_path)
        else:
            text, confidence = process_image(file_path)
        
        if confidence < settings.MIN_CONFIDENCE:
            raise ValueError(f"Low OCR confidence: {confidence}%")
        
        file_hash = generate_file_hash(file_path)
        query = Document.__table__.insert().values(
            filename=os.path.basename(file_path),
            file_type="pdf" if file_path.endswith(".pdf") else "image",
            text_content=text,
            ocr_confidence=confidence,
            file_hash=file_hash
        )
        await database.execute(query)
        
        return {"status": "success", "file": file_path}
    
    except Exception as e:
        return {"status": "error", "file": file_path, "error": str(e)}
