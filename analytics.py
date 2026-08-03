"""
analytics.py
---------------------------------------------------------
Enterprise Document Intelligence Platform
Analytics Module
---------------------------------------------------------
"""

from __future__ import annotations

from collections import Counter
from typing import List, Dict, Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================================================
# Dashboard Metrics
# =========================================================

def dashboard_metrics(documents, searches) -> Dict[str, Any]:
    """
    Calculate dashboard KPI metrics.
    """

    total_documents = len(documents)
    total_searches = len(searches)

    total_storage = sum(
        getattr(doc, "filesize", 0) or 0
        for doc in documents
    )

    total_words = sum(
        len((getattr(doc, "extracted_text", "") or "").split())
        for doc in documents
    )

    average_size = (
        total_storage / total_documents
        if total_documents
        else 0
    )

    return {
        "documents": total_documents,
        "searches": total_searches,
        "storage": round(total_storage, 2),
        "words": total_words,
        "average_size": round(average_size, 2),
    }


# =========================================================
# File Type Distribution
# =========================================================

def file_distribution(documents) -> pd.DataFrame:

    counter = Counter()

    for doc in documents:

        filetype = getattr(doc, "filetype", "Unknown")

        if not filetype:
            filetype = "Unknown"

        counter[filetype] += 1

    if not counter:

        return pd.DataFrame(
            columns=["File Type", "Count"]
        )

    return pd.DataFrame({

        "File Type": list(counter.keys()),

        "Count": list(counter.values())

    })


# =========================================================
# Upload Timeline
# =========================================================

def upload_timeline(documents):

    counter = Counter()

    for doc in documents:

        if getattr(doc, "upload_time", None):

            counter[
                doc.upload_time.date()
            ] += 1

    if not counter:

        return pd.DataFrame(
            columns=[
                "Date",
                "Uploads"
            ]
        )

    df = pd.DataFrame({

        "Date": list(counter.keys()),

        "Uploads": list(counter.values())

    })

    return df.sort_values(
        "Date"
    )


# =========================================================
# Largest Documents
# =========================================================

def largest_documents(
    documents,
    top: int = 10
):

    docs = sorted(

        documents,

        key=lambda x:
        getattr(
            x,
            "filesize",
            0
        ) or 0,

        reverse=True

    )

    return docs[:top]


# =========================================================
# Search Statistics
# =========================================================

def search_statistics(
    searches
):

    successful = sum(

        1

        for s in searches

        if getattr(
            s,
            "results_found",
            0
        ) > 0

    )

    failed = len(searches) - successful

    return {

        "success": successful,

        "failed": failed,

        "total": len(searches)

    }


# =========================================================
# Search Timeline
# =========================================================

def search_trend(
    searches
):

    counter = Counter()

    for s in searches:

        if getattr(
            s,
            "searched_at",
            None
        ):

            counter[
                s.searched_at.date()
            ] += 1

    if not counter:

        return pd.DataFrame(

            columns=[
                "Date",
                "Searches"
            ]

        )

    df = pd.DataFrame({

        "Date": list(counter.keys()),

        "Searches": list(counter.values())

    })

    return df.sort_values(
        "Date"
    )
# =========================================================
# File Distribution Chart
# =========================================================

def file_distribution_chart(documents):

    df = file_distribution(documents)

    if df.empty:

        fig = go.Figure()

        fig.update_layout(
            title="File Type Distribution"
        )

        return fig

    fig = px.pie(
        df,
        names="File Type",
        values="Count",
        hole=0.45
    )

    fig.update_layout(
        title="📂 File Type Distribution",
        legend_title="File Types"
    )

    return fig


# =========================================================
# Upload Trend Chart
# =========================================================

def upload_chart(documents):

    df = upload_timeline(documents)

    if df.empty:

        fig = go.Figure()

        fig.update_layout(
            title="Upload Trend"
        )

        return fig

    fig = px.line(
        df,
        x="Date",
        y="Uploads",
        markers=True
    )

    fig.update_traces(
        line_width=3,
        marker_size=8
    )

    fig.update_layout(
        title="📈 Upload Trend",
        xaxis_title="Date",
        yaxis_title="Documents Uploaded"
    )

    return fig


# =========================================================
# Storage Usage Chart
# =========================================================

def storage_chart(documents):

    docs = largest_documents(documents)

    if not docs:

        fig = go.Figure()

        fig.update_layout(
            title="Storage Usage"
        )

        return fig

    df = pd.DataFrame({

        "Document":[d.title for d in docs],

        "Size":[
            getattr(d, "filesize", 0) or 0
            for d in docs
        ]

    })

    fig = px.bar(

        df,

        x="Document",

        y="Size"

    )

    fig.update_layout(

        title="💾 Largest Documents",

        xaxis_title="Document",

        yaxis_title="Size (MB)"

    )

    return fig


# =========================================================
# Word Count Chart
# =========================================================

def word_count_chart(documents):

    if not documents:

        fig = go.Figure()

        fig.update_layout(
            title="Word Count"
        )

        return fig

    df = pd.DataFrame({

        "Document":[d.title for d in documents],

        "Words":[

            len(

                (
                    getattr(
                        d,
                        "extracted_text",
                        ""
                    ) or ""
                ).split()

            )

            for d in documents

        ]

    })

    fig = px.bar(

        df,

        x="Document",

        y="Words"

    )

    fig.update_layout(

        title="📝 Word Count",

        xaxis_title="Document",

        yaxis_title="Words"

    )

    return fig


# =========================================================
# Search Activity Chart
# =========================================================

def search_chart(searches):

    df = search_trend(searches)

    if df.empty:

        fig = go.Figure()

        fig.update_layout(
            title="Search Activity"
        )

        return fig

    fig = px.area(

        df,

        x="Date",

        y="Searches"

    )

    fig.update_layout(

        title="🔍 Search Activity",

        xaxis_title="Date",

        yaxis_title="Searches"

    )

    return fig


# =========================================================
# Top Search Keywords
# =========================================================

def top_keywords(
    searches,
    limit=15
):

    words = []

    for s in searches:

        query = getattr(
            s,
            "query",
            ""
        )

        words.extend(
            query.lower().split()
        )

    return Counter(words).most_common(limit)
# =========================================================
# Document Statistics
# =========================================================

def document_statistics(documents):

    if not documents:
        return {}

    total_pages = sum(
        getattr(doc, "pages", 0) or 0
        for doc in documents
    )

    total_storage = sum(
        getattr(doc, "filesize", 0) or 0
        for doc in documents
    )

    total_words = sum(
        len(
            (getattr(doc, "extracted_text", "") or "").split()
        )
        for doc in documents
    )

    avg_pages = total_pages / len(documents)
    avg_words = total_words / len(documents)

    return {
        "total_pages": total_pages,
        "total_storage": round(total_storage, 2),
        "total_words": total_words,
        "average_pages": round(avg_pages, 2),
        "average_words": round(avg_words, 2),
    }


# =========================================================
# Most Common File Types
# =========================================================

def most_common_filetypes(documents, limit=5):

    counter = Counter()

    for doc in documents:

        filetype = getattr(doc, "filetype", "Unknown") or "Unknown"

        counter[filetype] += 1

    return counter.most_common(limit)


# =========================================================
# User Activity Summary
# =========================================================

def user_activity_summary(documents, searches):

    metrics = dashboard_metrics(documents, searches)
    search_stats = search_statistics(searches)
    doc_stats = document_statistics(documents)

    return {

        "documents": metrics["documents"],

        "searches": metrics["searches"],

        "storage_mb": metrics["storage"],

        "words": metrics["words"],

        "successful_searches": search_stats["success"],

        "failed_searches": search_stats["failed"],

        "pages": doc_stats.get("total_pages", 0)

    }


# =========================================================
# Analytics Report DataFrame
# =========================================================

def analytics_report(documents, searches):

    metrics = dashboard_metrics(
        documents,
        searches
    )

    stats = document_statistics(
        documents
    )

    search_stats = search_statistics(
        searches
    )

    report = pd.DataFrame({

        "Metric": [

            "Documents",

            "Searches",

            "Successful Searches",

            "Failed Searches",

            "Storage (MB)",

            "Pages",

            "Words",

            "Average Size (MB)",

            "Average Pages",

            "Average Words"

        ],

        "Value": [

            metrics["documents"],

            metrics["searches"],

            search_stats["success"],

            search_stats["failed"],

            metrics["storage"],

            stats.get("total_pages", 0),

            stats.get("total_words", 0),

            metrics["average_size"],

            stats.get("average_pages", 0),

            stats.get("average_words", 0)

        ]

    })

    return report


# =========================================================
# Export CSV
# =========================================================

def export_csv(documents, searches):

    report = analytics_report(
        documents,
        searches
    )

    return report.to_csv(
        index=False
    ).encode("utf-8")


# =========================================================
# Dashboard Summary
# =========================================================

def analytics_summary(documents, searches):

    return {

        "metrics":
            dashboard_metrics(
                documents,
                searches
            ),

        "document_statistics":
            document_statistics(
                documents
            ),

        "search_statistics":
            search_statistics(
                searches
            ),

        "file_distribution":
            file_distribution(
                documents
            ),

        "upload_timeline":
            upload_timeline(
                documents
            ),

        "search_timeline":
            search_trend(
                searches
            ),

        "top_keywords":
            top_keywords(
                searches
            ),

        "common_filetypes":
            most_common_filetypes(
                documents
            )

    }


# =========================================================
# Module Test
# =========================================================

if __name__ == "__main__":

    print(
        "Enterprise Document Intelligence Platform"
    )

    print(
        "Analytics Module Loaded Successfully."
    )