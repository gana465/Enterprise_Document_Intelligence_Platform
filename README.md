# Enterprise Document Intelligence Platform (EDIP)

## 📌 Overview

The **Enterprise Document Intelligence Platform (EDIP)** is an AI-powered document management system that enables users to upload, organize, search, summarize, and analyze documents efficiently. It combines **OCR, Natural Language Processing (NLP), Semantic Search, and Analytics** to provide intelligent document retrieval and management.

---

# 🚀 Features

* 🔐 User Authentication (Login & Registration)
* 📤 Upload PDF, DOCX, and TXT documents
* 📄 Automatic Text Extraction
* 🤖 AI-Powered Document Summarization
* 🔍 Semantic Search using Sentence Transformers
* 📊 Interactive Analytics Dashboard
* 📁 Document Management
* 📥 Download Original Documents
* 🗑️ Delete Documents
* 📈 Search History
* 💾 SQLite Database Support

---

# 🛠️ Technologies Used

### Frontend

* Streamlit

### Backend

* Python

### Database

* SQLite
* SQLAlchemy

### Artificial Intelligence

* Sentence Transformers
* Hugging Face Transformers
* Scikit-learn

### OCR & Document Processing

* Tesseract OCR
* PyMuPDF
* python-docx

### Visualization

* Plotly
* Pandas

---

# 📂 Supported File Formats

* PDF
* DOCX
* TXT

---

# 📁 Project Structure

```
Enterprise_Document_Intelligence_Platform/
│
├── app.py
├── config.py
├── database.py
├── models.py
├── auth.py
├── utils.py
├── semantic_search.py
├── summarizer.py
├── analytics.py
├── ocr.py
├── requirements.txt
├── README.md
│
├── uploads/
├── embeddings/
├── reports/
├── static/
└── assets/
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/your-username/Enterprise-Document-Intelligence-Platform.git
cd Enterprise-Document-Intelligence-Platform
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

---

# 🔄 Workflow

1. User logs into the application.
2. Uploads a document (PDF, DOCX, or TXT).
3. The system extracts text from the document.
4. AI generates a concise summary.
5. A semantic embedding is created and stored.
6. Document metadata is saved in the SQLite database.
7. Users search using natural language.
8. Semantic Search retrieves the most relevant documents.
9. Analytics Dashboard displays document insights and statistics.

---

# 📊 Analytics

The dashboard provides:

* Total Documents
* Total Searches
* Storage Usage
* Word Count
* Average Document Size
* Upload Timeline
* File Type Distribution
* Search Statistics

---

# 📸 Screenshots

Add screenshots of the following pages:

* Login Page
* Dashboard
* Upload Module
* Semantic Search
* Analytics Dashboard
* Document Management

---

# 🔮 Future Enhancements

* Cloud Storage Integration
* Multi-language Support
* Role-Based Access Control
* AI Chatbot for Document Q&A
* Google Drive Integration
* Microsoft SharePoint Integration

---

# 👨‍💻 Author

**Baddula Venkata Sai Ganapathi Naidu**

B.Tech – CSE (Artificial Intelligence & Machine Learning)

---

# 📄 License

This project is developed for academic and educational purposes.
