"""
ocr.py
-----------------------------------------------------
OCR Engine
Enterprise Document Intelligence Platform
-----------------------------------------------------
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import cv2
import fitz
import numpy as np
import pytesseract

from PIL import Image

from config import OCR_LANGUAGE, TESSERACT_PATH


# ---------------------------------------------------
# Configure Tesseract (Windows)
# ---------------------------------------------------

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ---------------------------------------------------
# Read Image
# ---------------------------------------------------

def load_image(path):

    image = cv2.imread(str(path))

    if image is None:
        raise FileNotFoundError(path)

    return image


# ---------------------------------------------------
# Grayscale
# ---------------------------------------------------

def to_gray(image):

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


# ---------------------------------------------------
# Noise Removal
# ---------------------------------------------------

def remove_noise(image):

    return cv2.medianBlur(
        image,
        3
    )


# ---------------------------------------------------
# Threshold
# ---------------------------------------------------

def threshold(image):

    return cv2.threshold(
        image,
        0,
        255,
        cv2.THRESH_BINARY +
        cv2.THRESH_OTSU
    )[1]


# ---------------------------------------------------
# Deskew
# ---------------------------------------------------

def deskew(image):

    coords = np.column_stack(
        np.where(image > 0)
    )

    if len(coords) == 0:
        return image

    angle = cv2.minAreaRect(
        coords
    )[-1]

    if angle < -45:
        angle = 90 + angle

    h, w = image.shape

    matrix = cv2.getRotationMatrix2D(
        (w // 2, h // 2),
        angle,
        1.0
    )

    return cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )


# ---------------------------------------------------
# Preprocess
# ---------------------------------------------------

def preprocess(path):

    image = load_image(path)

    image = to_gray(image)

    image = remove_noise(image)

    image = threshold(image)

    image = deskew(image)

    return image


# ---------------------------------------------------
# OCR Image
# ---------------------------------------------------

def image_to_text(path):

    processed = preprocess(path)

    return pytesseract.image_to_string(
        processed,
        lang=OCR_LANGUAGE
    )


# ---------------------------------------------------
# OCR Confidence
# ---------------------------------------------------

def image_confidence(path):

    processed = preprocess(path)

    data = pytesseract.image_to_data(
        processed,
        output_type=pytesseract.Output.DICT
    )

    values = []

    for c in data["conf"]:

        try:

            c = float(c)

            if c >= 0:
                values.append(c)

        except Exception:
            pass

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        2
    )


# ---------------------------------------------------
# PDF Has Text?
# ---------------------------------------------------

def pdf_has_text(pdf_path):

    doc = fitz.open(pdf_path)

    for page in doc:

        if page.get_text().strip():

            doc.close()

            return True

    doc.close()

    return False


# ---------------------------------------------------
# Extract Digital PDF
# ---------------------------------------------------

def digital_pdf_text(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:

        text += page.get_text()

    doc.close()

    return text


# ---------------------------------------------------
# OCR Scanned PDF
# ---------------------------------------------------

def scanned_pdf_text(pdf_path):

    doc = fitz.open(pdf_path)

    output = []

    for page in doc:

        pix = page.get_pixmap(
            dpi=300
        )

        with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        ) as tmp:

            pix.save(tmp.name)

            output.append(
                image_to_text(tmp.name)
            )

    doc.close()

    return "\n".join(output)


# ---------------------------------------------------
# Auto Extract
# ---------------------------------------------------

def extract_text(file_path):

    extension = Path(file_path).suffix.lower()

    if extension in [

        ".png",

        ".jpg",

        ".jpeg"

    ]:

        return image_to_text(file_path)

    if extension == ".pdf":

        if pdf_has_text(file_path):

            return digital_pdf_text(file_path)

        return scanned_pdf_text(file_path)

    return ""


# ---------------------------------------------------
# OCR Report
# ---------------------------------------------------

def ocr_report(image_path):

    text = image_to_text(image_path)

    return {

        "characters": len(text),

        "words": len(text.split()),

        "confidence": image_confidence(image_path)

    }