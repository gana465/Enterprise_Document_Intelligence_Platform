"""
app.py
-------------------------------------------------------
Enterprise Document Intelligence Platform
Main Streamlit Application
-------------------------------------------------------
"""

from pathlib import Path
import streamlit as st
import pandas as pd

from sqlalchemy import desc

from config import (
    APP_NAME,
    APP_VERSION,
    PAGE_ICON,
    PAGE_TITLE,
    LAYOUT,
    SIDEBAR_STATE,
    WELCOME_MESSAGE
)

from database import init_db, session_scope

from models import (
    User,
    Document,
    SearchHistory
)

from auth import (
    authenticate_user,
    register_user
)

from utils import (
    allowed_file,
    sanitize_filename,
    save_uploaded_file,
    extract_text,
    clean_text,
    metadata
)

from ocr import extract_text as ocr_extract

from summarizer import summarize

from semantic_search import (
    build_document_embedding,
    semantic_search
)

from analytics import (
    dashboard_metrics,
    file_distribution_chart,
    upload_chart,
    storage_chart,
    word_count_chart,
    search_chart
)

# -------------------------------------------------------
# Streamlit Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE
)

# -------------------------------------------------------
# Initialize Database
# -------------------------------------------------------

init_db()

# -------------------------------------------------------
# Session State
# -------------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------------------------------------------
# Custom CSS
# -------------------------------------------------------

st.markdown("""
<style>

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

.block-container{
    padding-top:1.2rem;
    padding-bottom:2rem;
}

.metric-card{
    background:white;
    padding:18px;
    border-radius:12px;
    box-shadow:0px 2px 10px rgba(0,0,0,0.08);
}

.login-box{

    max-width:500px;

    margin:auto;

    padding:30px;

    background:white;

    border-radius:15px;

    box-shadow:0 5px 20px rgba(0,0,0,.12);

}

.sidebar-title{

    font-size:22px;

    font-weight:bold;

}

.success-box{

    padding:10px;

    background:#E8F5E9;

    border-radius:10px;

}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# Helper
# -------------------------------------------------------

def current_user():

    if not st.session_state.logged_in:
        return None

    with session_scope() as db:

        return (
            db.query(User)
            .filter(User.id == st.session_state.user_id)
            .first()
        )

# -------------------------------------------------------
# Login Screen
# -------------------------------------------------------

def login_screen():

    st.title(APP_NAME)

    st.caption(APP_VERSION)

    st.info(WELCOME_MESSAGE)

    tab1, tab2 = st.tabs(
        ["Login", "Register"]
    )

    # ---------------- Login ----------------

    with tab1:

        username = st.text_input(
            "Username",
            key="login_user"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_pass"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            user = authenticate_user(
                username,
                password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user_id = user.id
                st.session_state.username = user.username

                st.success(
                    f"Welcome {user.username}"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    # ---------------- Register ----------------

    with tab2:

        new_username = st.text_input(
            "Username",
            key="reg_user"
        )

        new_email = st.text_input(
            "Email",
            key="reg_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="reg_pass"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            ok, message = register_user(
                new_username,
                new_email,
                new_password
            )

            if ok:
                st.success(message)
            else:
                st.error(message)

# -------------------------------------------------------
# Stop if not logged in
# -------------------------------------------------------

if not st.session_state.logged_in:

    login_screen()

    st.stop()

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

st.sidebar.title("📚 EDIP")

st.sidebar.write(
    f"**User:** {st.session_state.username}"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📤 Upload",
        "🔍 Semantic Search",
        "📁 Documents",
        "📊 Analytics",
        "⚙️ Settings",
        "ℹ️ About",
        "🚪 Logout"
    ]
)

if page == "🚪 Logout":

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""

    st.rerun()
# =====================================================
# DASHBOARD
# =====================================================

if page == "🏠 Dashboard":

    st.title("🏠 Dashboard")

    with session_scope() as db:

        user = current_user()

        documents = (
            db.query(Document)
            .filter(
                Document.owner_id == user.id
            )
            .order_by(
                desc(Document.upload_time)
            )
            .all()
        )

        searches = (
            db.query(SearchHistory)
            .filter(
                SearchHistory.user_id == user.id
            )
            .order_by(
                desc(SearchHistory.searched_at)
            )
            .all()
        )

    # ------------------------------------------
    # KPI CARDS
    # ------------------------------------------

    metrics = dashboard_metrics(
        documents,
        searches
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Documents",
        metrics["documents"]
    )

    c2.metric(
        "Searches",
        metrics["searches"]
    )

    c3.metric(
        "Storage",
        f'{metrics["storage"]:.2f} MB'
    )

    c4.metric(
        "Words",
        f'{metrics["words"]:,}'
    )

    c5.metric(
        "Average Size",
        f'{metrics["average_size"]:.2f} MB'
    )

    st.divider()

    # ------------------------------------------
    # CHARTS
    # ------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.plotly_chart(

            file_distribution_chart(
                documents
            ),

            use_container_width=True

        )

    with col2:

        st.plotly_chart(

            upload_chart(
                documents
            ),

            use_container_width=True

        )

    col3, col4 = st.columns(2)

    with col3:

        st.plotly_chart(

            storage_chart(
                documents
            ),

            use_container_width=True

        )

    with col4:

        st.plotly_chart(

            word_count_chart(
                documents
            ),

            use_container_width=True

        )

    st.divider()

    # ------------------------------------------
    # RECENT DOCUMENTS
    # ------------------------------------------

    st.subheader("📄 Recent Documents")

    if not documents:

        st.info(
            "No documents uploaded yet."
        )

    else:

        for doc in documents[:10]:

            with st.expander(doc.title):

                c1, c2 = st.columns(2)

                c1.write(
                    f"**Filename:** {doc.filename}"
                )

                c2.write(
                    f"**Type:** {doc.filetype}"
                )

                c1.write(
                    f"**Size:** {doc.filesize:.2f} MB"
                )

                c2.write(
                    f"**Pages:** {doc.pages}"
                )

                st.caption(
                    doc.upload_time.strftime(
                        "%d %b %Y %H:%M"
                    )
                )

                if doc.summary:

                    st.markdown("### AI Summary")

                    st.write(doc.summary)

                else:

                    st.warning(
                        "Summary not available."
                    )

    st.divider()

    # ------------------------------------------
    # RECENT SEARCHES
    # ------------------------------------------

    st.subheader(
        "🔍 Recent Searches"
    )

    if not searches:

        st.info(
            "No searches performed."
        )

    else:

        history = []

        for s in searches[:10]:

            history.append(

                {

                    "Query": s.query,

                    "Results": s.results_found,

                    "Similarity":

                        round(
                            s.similarity_score,
                            3
                        ),

                    "Time":

                        s.searched_at.strftime(
                            "%d-%m-%Y %H:%M"
                        )

                }

            )

        st.dataframe(

            pd.DataFrame(history),

            use_container_width=True

        )

    st.divider()

    # ------------------------------------------
    # QUICK INSIGHTS
    # ------------------------------------------

    st.subheader("📌 Quick Insights")

    if documents:

        total_pdf = len(

            [

                d

                for d in documents

                if d.filetype.lower()

                == ".pdf"

            ]

        )

        total_docx = len(

            [

                d

                for d in documents

                if d.filetype.lower()

                == ".docx"

            ]

        )

        total_txt = len(

            [

                d

                for d in documents

                if d.filetype.lower()

                == ".txt"

            ]

        )

        a, b, c = st.columns(3)

        a.success(
            f"📕 PDFs : {total_pdf}"
        )

        b.info(
            f"📘 DOCX : {total_docx}"
        )

        c.warning(
            f"📄 TXT : {total_txt}"
        )

    else:

        st.info(
            "Upload documents to see analytics."
        )
# =====================================================
# UPLOAD DOCUMENTS
# =====================================================

if page == "📤 Upload":

    st.title("📤 Upload Documents")

    st.markdown("""
    Upload your documents to enable:

    - 📄 Automatic text extraction
    - 🔍 Semantic search
    - 🤖 AI-powered summarization
    - 📊 Analytics
    """)

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=[
            "pdf",
            "docx",
            "txt",
            "png",
            "jpg",
            "jpeg"
        ]
    )

    generate_summary = st.checkbox(
        "Generate AI Summary",
        value=True
    )

    generate_embedding = st.checkbox(
        "Generate Semantic Embedding",
        value=True
    )

    if uploaded_file is not None:

        filename = sanitize_filename(
            uploaded_file.name
        )

        st.subheader("📋 File Details")

        file_info = {
            "Filename": filename,
            "Size (MB)": round(
                uploaded_file.size / (1024 * 1024),
                2
            ),
            "Extension": Path(filename).suffix.lower()
        }

        st.table(
            pd.DataFrame(
                file_info.items(),
                columns=["Property", "Value"]
            )
        )

        if not allowed_file(filename):

            st.error(
                "Unsupported file type."
            )

            st.stop()

        if st.button(
            "🚀 Process Document",
            use_container_width=True
        ):

            progress = st.progress(0)

            status = st.empty()

            try:

                # ---------------------------------
                # Step 1
                # ---------------------------------

                status.info(
                    "Saving uploaded file..."
                )

                progress.progress(10)

                saved_path = save_uploaded_file(
                    uploaded_file
                )

                progress.progress(20)

                # ---------------------------------
                # Duplicate Check
                # ---------------------------------

                with session_scope() as db:

                    existing = (
                        db.query(Document)
                        .filter(
                            Document.filename == filename,
                            Document.owner_id == st.session_state.user_id
                        )
                        .first()
                    )

                    if existing:

                        st.warning(
                            "This document already exists."
                        )

                        st.stop()

                progress.progress(30)

                # ---------------------------------
                # Metadata
                # ---------------------------------

                status.info(
                    "Reading metadata..."
                )

                meta = metadata(saved_path)

                progress.progress(40)

                # ---------------------------------
                # Text Extraction
                # ---------------------------------

                status.info(
                    "Extracting text..."
                )

                extension = Path(saved_path).suffix.lower()

                if extension in [".pdf", ".png", ".jpg", ".jpeg"]:

                    extracted_text = ocr_extract(
                        saved_path
                    )

                else:

                    extracted_text = extract_text(
                        saved_path
                    )

                extracted_text = clean_text(
                    extracted_text
                )

                progress.progress(60)

                if len(extracted_text.strip()) == 0:

                    st.error(
                        "No readable text found."
                    )

                    st.stop()
                # ---------------------------------
                # AI Summary
                # ---------------------------------

                document_summary = ""

                if generate_summary:

                    status.info(
                        "Generating AI summary..."
                    )

                    progress.progress(70)

                    try:

                        document_summary = summarize(
                            extracted_text
                        )

                    except Exception as e:

                        st.warning(
                            f"Summary generation failed: {e}"
                        )

                        document_summary = ""

                # ---------------------------------
                # Semantic Embedding
                # ---------------------------------

                embedding_created = False

                if generate_embedding:

                    status.info("Generating semantic embedding...")

                    progress.progress(80)

                    try:
                        # Save the document first to get its ID
                        with session_scope() as db:

                            new_document = Document(
                                title=Path(filename).stem,
                                filename=filename,
                                filepath=str(saved_path),
                                filetype=Path(filename).suffix.lower(),
                                filesize=meta.get("size", 0),
                                pages=meta.get("pages", 1),
                                extracted_text=extracted_text,
                                summary=document_summary,
                                embedding_created=False,
                                owner_id=st.session_state.user_id
                            )

                            db.add(new_document)
                            db.commit()
                            db.refresh(new_document)

                            embedding_created = build_document_embedding(
                                new_document.id,
                                extracted_text
                            )

                            new_document.embedding_created = embedding_created
                            db.commit()

                    except Exception as e:
                        st.error(f"Embedding generation failed: {e}")
                # ---------------------------------
                # Save to Database
                # ---------------------------------

                status.info(
                    "Saving document information..."
                )

                progress.progress(90)

                with session_scope() as db:

                    new_document = Document(

                        title=Path(filename).stem,

                        filename=filename,

                        filepath=str(saved_path),

                        filetype=Path(filename).suffix.lower(),

                        filesize=meta.get(
                            "size",
                            0
                        ),

                        pages=meta.get(
                            "pages",
                            1
                        ),

                        extracted_text=extracted_text,

                        summary=document_summary,

                        embedding_created=embedding_created,

                        owner_id=st.session_state.user_id

                    )

                    db.add(new_document)

                progress.progress(100)

                status.success(
                    "Document processed successfully."
                )

                st.success(
                    "✅ Upload completed successfully!"
                )


                # ---------------------------------
                # Preview
                # ---------------------------------

                with st.expander(
                    "📄 Extracted Text Preview"
                ):

                    st.text_area(

                        "Text",

                        extracted_text[:5000],

                        height=250

                    )

                if document_summary:

                    with st.expander(
                        "🤖 AI Summary"
                    ):

                        st.write(
                            document_summary
                        )

            except Exception as e:

                st.exception(e)

# =====================================================
# SEMANTIC SEARCH
# =====================================================

if page == "🔍 Semantic Search":

    st.title("🔍 Semantic Search")

    st.markdown("""
Search your uploaded documents using **natural language** instead of exact keywords.

Examples:
- "Annual financial report"
- "Machine learning project"
- "Employee leave policy"
- "AI healthcare research"
    """)

    query = st.text_input(
        "Enter your search query",
        placeholder="Search documents..."
    )

    similarity_threshold = st.slider(
        "Minimum Similarity Score",
        min_value=0.0,
        max_value=1.0,
        value=0.40,
        step=0.05
    )

    max_results = st.slider(
        "Maximum Results",
        min_value=1,
        max_value=20,
        value=5
    )

    if st.button(
        "🔍 Search",
        use_container_width=True
    ):

        if not query.strip():

            st.warning(
                "Please enter a search query."
            )

            st.stop()

        with st.spinner("Searching documents..."):

            try:

                from database import SessionLocal
                from models import Document

                db = SessionLocal()

                documents = db.query(Document).all()

                results = semantic_search(
                    query=query,
                    documents=documents,
                    top_k=max_results
                )

                db.close()

            except Exception as e:

                st.error(
                    f"Search failed: {e}"
                )

                st.stop()

        if not results:

            st.info(
                "No matching documents found."
            )

            # Log unsuccessful search
            with session_scope() as db:

                history = SearchHistory(

                    query=query,

                    similarity_score=0.0,

                    results_found=0,

                    user_id=st.session_state.user_id

                )

                db.add(history)

            st.stop()

        filtered_results = []

        for result in results:

            score = result.get("score", 0)

            if score >= similarity_threshold:

                filtered_results.append(result)

        st.success(
            f"Found {len(filtered_results)} matching document(s)."
        )
        # -----------------------------------------
        # Save Search History
        # -----------------------------------------

        highest_score = max(
            [r.get("score", 0) for r in filtered_results],
            default=0.0
        )

        with session_scope() as db:

            history = SearchHistory(

                query=query,

                similarity_score=highest_score,

                results_found=len(filtered_results),

                user_id=st.session_state.user_id

            )

            db.add(history)

        st.divider()

        st.subheader("📄 Search Results")

        # -----------------------------------------
        # Display Results
        # -----------------------------------------

        for index, result in enumerate(filtered_results, start=1):

            document_id = result.get("document_id")

            similarity = result.get("score", 0)

            with session_scope() as db:

                document = (
                    db.query(Document)
                    .filter(Document.id == document_id)
                    .first()
                )

            if document is None:
                continue

            with st.expander(
                f"{index}. {document.title}"
            ):

                col1, col2 = st.columns([3, 1])

                with col1:

                    st.write(
                        f"**Filename:** {document.filename}"
                    )

                    st.write(
                        f"**Type:** {document.filetype}"
                    )

                    st.write(
                        f"**Pages:** {document.pages}"
                    )

                    st.write(
                        f"**Uploaded:** {document.upload_time.strftime('%d %b %Y %H:%M')}"
                    )

                with col2:

                    st.metric(
                        "Similarity",
                        f"{similarity:.3f}"
                    )

                st.progress(
                    min(similarity, 1.0)
                )

                # -----------------------------------------
                # AI Summary
                # -----------------------------------------

                if document.summary:

                    st.markdown("### 🤖 AI Summary")

                    st.write(document.summary)

                # -----------------------------------------
                # Text Preview
                # -----------------------------------------

                st.markdown("### 📄 Preview")

                preview = document.extracted_text[:1200]

                st.text_area(

                    "Extracted Text",

                    preview,

                    height=220,

                    key=f"text_{document.id}"

                )

                # -----------------------------------------
                # Download
                # -----------------------------------------

                try:

                    with open(document.filepath, "rb") as file:

                        st.download_button(

                            label="📥 Download Original",

                            data=file,

                            file_name=document.filename,

                            key=f"download_{document.id}"

                        )

                except Exception:

                    st.warning(
                        "Original file is unavailable."
                    )
# =====================================================
# DOCUMENT MANAGEMENT
# =====================================================

if page == "📁 Documents":

    st.title("📁 My Documents")

    search_text = st.text_input(
        "Search by title or filename",
        placeholder="Enter document name..."
    )

    refresh = st.button(
        "🔄 Refresh"
    )

    with session_scope() as db:

        documents = (
            db.query(Document)
            .filter(
                Document.owner_id == st.session_state.user_id
            )
            .order_by(
                desc(Document.upload_time)
            )
            .all()
        )

    # -----------------------------------------
    # Filter Documents
    # -----------------------------------------

    if search_text.strip():

        keyword = search_text.lower()

        documents = [

            doc

            for doc in documents

            if keyword in doc.title.lower()

            or keyword in doc.filename.lower()

        ]

    st.write(f"**Total Documents:** {len(documents)}")

    if not documents:

        st.info("No documents found.")

    else:

        for document in documents:

            with st.expander(
                f"📄 {document.title}"
            ):

                left, right = st.columns([3, 1])

                with left:

                    st.write(
                        f"**Filename:** {document.filename}"
                    )

                    st.write(
                        f"**Type:** {document.filetype}"
                    )

                    st.write(
                        f"**Pages:** {document.pages}"
                    )

                    st.write(
                        f"**Size:** {document.filesize:.2f} MB"
                    )

                    st.write(
                        f"**Uploaded:** {document.upload_time.strftime('%d %b %Y %H:%M')}"
                    )

                with right:

                    st.metric(
                        "Embedding",
                        "✅"
                        if document.embedding_created
                        else "❌"
                    )

                if document.summary:

                    st.markdown("### 🤖 AI Summary")

                    st.write(document.summary)

                st.markdown("### 📄 Extracted Text")

                st.text_area(

                    "Content",

                    document.extracted_text,

                    height=250,

                    key=f"doc_text_{document.id}"

                )
                # -----------------------------------------
                # Actions
                # -----------------------------------------

                st.markdown("### ⚙️ Actions")

                col_download, col_delete = st.columns(2)

                # ---------------- Download ----------------

                with col_download:

                    try:

                        with open(document.filepath, "rb") as file:

                            st.download_button(

                                label="📥 Download",

                                data=file.read(),

                                file_name=document.filename,

                                mime="application/octet-stream",

                                key=f"download_doc_{document.id}"

                            )

                    except FileNotFoundError:

                        st.error(
                            "Original file not found."
                        )

                # ---------------- Delete ----------------

                with col_delete:

                    if st.button(

                        "🗑 Delete",

                        type="primary",

                        key=f"delete_doc_{document.id}"

                    ):

                        try:

                            # Delete embedding if available
                            if document.embedding_created:

                                try:

                                    from semantic_search import delete_embedding

                                    delete_embedding(document.id)

                                except Exception:
                                    pass

                            # Delete uploaded file
                            file_path = Path(document.filepath)

                            if file_path.exists():

                                file_path.unlink()

                            # Delete database record
                            with session_scope() as db:

                                db_doc = (

                                    db.query(Document)

                                    .filter(

                                        Document.id == document.id

                                    )

                                    .first()

                                )

                                if db_doc:

                                    db.delete(db_doc)

                            st.success(
                                "Document deleted successfully."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Deletion failed: {e}"
                            )
# =====================================================
# ANALYTICS
# =====================================================

if page == "📊 Analytics":

    st.title("📊 Analytics Dashboard")

    with session_scope() as db:

        documents = (
            db.query(Document)
            .filter(
                Document.owner_id == st.session_state.user_id
            )
            .all()
        )

        searches = (
            db.query(SearchHistory)
            .filter(
                SearchHistory.user_id == st.session_state.user_id
            )
            .all()
        )

    metrics = dashboard_metrics(
        documents,
        searches
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric(
        "Documents",
        metrics["documents"]
    )

    m2.metric(
        "Searches",
        metrics["searches"]
    )

    m3.metric(
        "Storage (MB)",
        f"{metrics['storage']:.2f}"
    )

    m4.metric(
        "Words",
        f"{metrics['words']:,}"
    )

    m5.metric(
        "Average Size",
        f"{metrics['average_size']:.2f} MB"
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        st.plotly_chart(
            file_distribution_chart(documents),
            use_container_width=True
        )

    with right:

        st.plotly_chart(
            upload_chart(documents),
            use_container_width=True
        )

    left, right = st.columns(2)

    with left:

        st.plotly_chart(
            storage_chart(documents),
            use_container_width=True
        )

    with right:

        st.plotly_chart(
            word_count_chart(documents),
            use_container_width=True
        )

    if searches:

        st.divider()

        st.plotly_chart(
            search_chart(searches),
            use_container_width=True
        )
    # -----------------------------------------------------
    # Search Statistics
    # -----------------------------------------------------

    st.divider()

    st.subheader("🔍 Search Statistics")

    stats = {
        "Successful": len(
            [s for s in searches if s.results_found > 0]
        ),
        "No Results": len(
            [s for s in searches if s.results_found == 0]
        )
    }

    c1, c2 = st.columns(2)

    c1.metric(
        "Successful Searches",
        stats["Successful"]
    )

    c2.metric(
        "No Result Searches",
        stats["No Results"]
    )

    # -----------------------------------------------------
    # Largest Documents
    # -----------------------------------------------------

    st.divider()

    st.subheader("📂 Largest Documents")

    if documents:

        largest_docs = sorted(
            documents,
            key=lambda d: d.filesize,
            reverse=True
        )[:10]

        largest_df = pd.DataFrame([
            {
                "Title": d.title,
                "Filename": d.filename,
                "Size (MB)": round(d.filesize, 2),
                "Pages": d.pages
            }
            for d in largest_docs
        ])

        st.dataframe(
            largest_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No uploaded documents."
        )

    # -----------------------------------------------------
    # Upload Timeline
    # -----------------------------------------------------

    st.divider()

    st.subheader("📅 Upload Timeline")

    if documents:

        timeline = pd.DataFrame([
            {
                "Document": d.title,
                "Uploaded": d.upload_time.strftime(
                    "%d %b %Y %H:%M"
                ),
                "Type": d.filetype
            }
            for d in sorted(
                documents,
                key=lambda x: x.upload_time,
                reverse=True
            )
        ])

        st.dataframe(
            timeline,
            use_container_width=True,
            hide_index=True
        )

    # -----------------------------------------------------
    # Recent Search History
    # -----------------------------------------------------

    st.divider()

    st.subheader("📝 Recent Search History")

    if searches:

        history = pd.DataFrame([
            {
                "Query": s.query,
                "Results": s.results_found,
                "Best Score": round(
                    s.similarity_score,
                    3
                ),
                "Time": s.searched_at.strftime(
                    "%d %b %Y %H:%M"
                )
            }
            for s in sorted(
                searches,
                key=lambda x: x.searched_at,
                reverse=True
            )[:20]
        ])

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No search history available."
        )

    # -----------------------------------------------------
    # Analytics Report
    # -----------------------------------------------------

    st.divider()

    st.subheader("📥 Export Analytics")

    report = pd.DataFrame({

        "Metric": [

            "Total Documents",

            "Total Searches",

            "Storage (MB)",

            "Average Size (MB)",

            "Total Words"

        ],

        "Value": [

            metrics["documents"],

            metrics["searches"],

            metrics["storage"],

            metrics["average_size"],

            metrics["words"]

        ]

    })

    csv = report.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        "📥 Download Analytics Report",

        csv,

        file_name="analytics_report.csv",

        mime="text/csv"

    )
# =====================================================
# SETTINGS
# =====================================================

if page == "⚙️ Settings":

    st.title("⚙️ Settings")

    user = current_user()

    st.subheader("👤 User Profile")

    st.text_input(
        "Username",
        value=user.username,
        disabled=True
    )

    st.text_input(
        "Email",
        value=user.email,
        disabled=True
    )

    st.text_input(
        "Role",
        value=user.role,
        disabled=True
    )

    st.caption(
        f"Account Created : {user.created_at.strftime('%d %b %Y')}"
    )

    st.divider()

    st.subheader("🎨 Preferences")

    show_summary = st.checkbox(
        "Generate summaries by default",
        value=True
    )

    show_embeddings = st.checkbox(
        "Generate embeddings by default",
        value=True
    )

    st.info(
        "These preferences are currently applied only during this session."
    )

    st.divider()

    st.subheader("🧹 Maintenance")

    if st.button(
        "Clear Search History"
    ):

        with session_scope() as db:

            db.query(SearchHistory).filter(

                SearchHistory.user_id == user.id

            ).delete()

        st.success(
            "Search history cleared."
        )

    st.divider()

    st.subheader("⚠️ Danger Zone")

    st.warning(
        "Bulk delete permanently removes every uploaded document."
    )

    if st.button(
        "Delete ALL Documents",
        type="primary"
    ):

        with session_scope() as db:

            docs = (

                db.query(Document)

                .filter(

                    Document.owner_id == user.id

                )

                .all()

            )

            deleted = 0

            for doc in docs:

                try:

                    path = Path(doc.filepath)

                    if path.exists():

                        path.unlink()

                except Exception:

                    pass

                try:

                    from semantic_search import delete_embedding

                    delete_embedding(doc.id)

                except Exception:

                    pass

                db.delete(doc)

                deleted += 1

        st.success(
            f"{deleted} document(s) deleted."
        )

        st.rerun()
# =====================================================
# ABOUT
# =====================================================

if page == "ℹ️ About":

    st.title("ℹ️ Enterprise Document Intelligence Platform")

    st.markdown("""
## Overview

Enterprise Document Intelligence Platform (EDIP) is an AI-powered document
management system that combines OCR, Natural Language Processing, semantic
search, and automatic summarization to help users organize and retrieve
information efficiently.

### Features

- 📄 Document Upload
- 🖼 OCR for Images & PDFs
- 🤖 AI Summarization
- 🔍 Semantic Search
- 📊 Analytics Dashboard
- 📁 Document Management
- 📥 Download & Export
- 👤 Multi-user Support

### Technology Stack

- Streamlit
- Python
- SQLAlchemy
- Sentence Transformers
- Hugging Face Transformers
- PyMuPDF
- OpenCV
- Tesseract OCR
- Plotly
""")

    st.divider()

    st.subheader("📦 Application Information")

    info = {
        "Application": APP_NAME,
        "Version": APP_VERSION,
        "Framework": "Streamlit",
        "Language": "Python",
        "Database": "SQLite + SQLAlchemy"
    }

    st.table(
        pd.DataFrame(
            info.items(),
            columns=["Property", "Value"]
        )
    )

    st.divider()

    st.caption(
        "Enterprise Document Intelligence Platform © 2026"
    )
