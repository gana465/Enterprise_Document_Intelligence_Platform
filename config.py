"""
config.py
----------------------------------------
Enterprise Document Intelligence Platform
Central Configuration File
----------------------------------------
"""

from pathlib import Path
import os

# -----------------------------------------------------
# Application Information
# -----------------------------------------------------

APP_NAME = "Enterprise Document Intelligence Platform"

APP_VERSION = "1.0.0"

APP_ICON = "📚"

AUTHOR = "Baddula Venkata Sai Ganapathi Naidu"

# -----------------------------------------------------
# Base Directory
# -----------------------------------------------------

from pathlib import Path

# ============================================
# Base Directories
# ============================================

BASE_DIR = Path(__file__).resolve().parent

UPLOADS_DIR = BASE_DIR / "uploads"
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
REPORTS_DIR = BASE_DIR / "reports"
STATIC_DIR = BASE_DIR / "static"
ASSETS_DIR = BASE_DIR / "assets"

# Create directories automatically
for folder in [
    UPLOADS_DIR,
    EMBEDDINGS_DIR,
    REPORTS_DIR,
    STATIC_DIR,
    ASSETS_DIR,
]:
    folder.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------
# Directories
# -----------------------------------------------------

UPLOAD_FOLDER = BASE_DIR / "uploads"

EMBEDDING_FOLDER = BASE_DIR / "embeddings"

REPORT_FOLDER = BASE_DIR / "reports"

STATIC_FOLDER = BASE_DIR / "static"

ASSET_FOLDER = BASE_DIR / "assets"

# Automatically create folders

for folder in [

    UPLOAD_FOLDER,

    EMBEDDING_FOLDER,

    REPORT_FOLDER,

    STATIC_FOLDER,

    ASSET_FOLDER

]:

    folder.mkdir(exist_ok=True)

# -----------------------------------------------------
# Database
# -----------------------------------------------------

DATABASE_URL = f"sqlite:///{BASE_DIR/'enterprise_documents.db'}"

# -----------------------------------------------------
# Authentication
# -----------------------------------------------------

PASSWORD_HASH_ALGORITHM = "bcrypt"

SESSION_TIMEOUT = 60 * 60

# -----------------------------------------------------
# Supported Files
# -----------------------------------------------------

SUPPORTED_EXTENSIONS = [

    ".pdf",

    ".docx",

    ".txt",

    ".png",

    ".jpg",

    ".jpeg"

]

MAX_UPLOAD_SIZE_MB = 100

# -----------------------------------------------------
# OCR
# -----------------------------------------------------

OCR_LANGUAGE = "eng"

TESSERACT_PATH = None

# Example:
#
# TESSERACT_PATH = (
#     r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# )

# -----------------------------------------------------
# Embedding Model
# -----------------------------------------------------

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# -----------------------------------------------------
# Summarization Model
# -----------------------------------------------------

SUMMARIZATION_MODEL = "facebook/bart-large-cnn"

SUMMARY_MAX_LENGTH = 150

SUMMARY_MIN_LENGTH = 40

# -----------------------------------------------------
# Semantic Search
# -----------------------------------------------------

TOP_K_RESULTS = 5

SIMILARITY_THRESHOLD = 0.40

# -----------------------------------------------------
# Dashboard
# -----------------------------------------------------

RECENT_DOCUMENTS = 10

TOP_KEYWORDS = 10

# -----------------------------------------------------
# Theme Colors
# -----------------------------------------------------

PRIMARY_COLOR = "#2563EB"

SECONDARY_COLOR = "#0F172A"

SUCCESS_COLOR = "#16A34A"

WARNING_COLOR = "#F59E0B"

ERROR_COLOR = "#DC2626"

BACKGROUND_COLOR = "#F8FAFC"

# -----------------------------------------------------
# Streamlit
# -----------------------------------------------------

PAGE_TITLE = APP_NAME

PAGE_ICON = APP_ICON

LAYOUT = "wide"

SIDEBAR_STATE = "expanded"

# -----------------------------------------------------
# Logging
# -----------------------------------------------------

LOG_LEVEL = "INFO"

# -----------------------------------------------------
# Application Banner
# -----------------------------------------------------

WELCOME_MESSAGE = """
Enterprise Document Intelligence Platform

AI-powered Semantic Search

AI Document Summarization

OCR Support

Analytics Dashboard
"""

# -----------------------------------------------------
# Version Info
# -----------------------------------------------------

ABOUT = {
    "Application": APP_NAME,
    "Version": APP_VERSION,
    "Author": AUTHOR,
    "AI": "Sentence Transformers + HuggingFace",
    "Database": "SQLite",
    "Framework": "Streamlit"
}