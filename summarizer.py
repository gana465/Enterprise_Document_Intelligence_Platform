"""
summarizer.py
-------------------------------------------------
AI Document Summarizer
Enterprise Document Intelligence Platform
-------------------------------------------------
"""

from __future__ import annotations

from transformers import pipeline

from config import (
    SUMMARIZATION_MODEL,
    SUMMARY_MAX_LENGTH,
    SUMMARY_MIN_LENGTH
)

# ---------------------------------------------------------
# Singleton Model
# ---------------------------------------------------------

_model = None


def get_model():
    """
    Load HuggingFace summarization model once.
    """

    global _model

    if _model is None:

        _model = pipeline(
            "summarization",
            model=SUMMARIZATION_MODEL
        )

    return _model


# ---------------------------------------------------------
# Split Long Documents
# ---------------------------------------------------------

def split_into_chunks(
    text: str,
    words_per_chunk: int = 700
):

    words = text.split()

    chunks = []

    for i in range(
        0,
        len(words),
        words_per_chunk
    ):

        chunk = " ".join(
            words[i:i + words_per_chunk]
        )

        chunks.append(chunk)

    return chunks


# ---------------------------------------------------------
# Summarize Chunk
# ---------------------------------------------------------

def summarize_chunk(
    chunk: str,
    max_length=SUMMARY_MAX_LENGTH,
    min_length=SUMMARY_MIN_LENGTH
):

    model = get_model()

    result = model(

        chunk,

        max_length=max_length,

        min_length=min_length,

        do_sample=False,

        truncation=True

    )

    return result[0]["summary_text"]


# ---------------------------------------------------------
# Recursive Summarization
# ---------------------------------------------------------

def summarize(text: str):

    if not text:

        return ""

    words = text.split()

    # Small documents
    if len(words) < 80:

        return text

    chunks = split_into_chunks(text)

    summaries = []

    for chunk in chunks:

        try:

            summaries.append(

                summarize_chunk(chunk)

            )

        except Exception:

            summaries.append(

                chunk[:400]

            )

    final = " ".join(summaries)

    # If summary is still too long,
    # summarize again.

    if len(final.split()) > 900:

        return summarize(final)

    return final


# ---------------------------------------------------------
# Summary Types
# ---------------------------------------------------------

def short_summary(text):

    summary = summarize(text)

    return " ".join(

        summary.split()[:50]

    )


def medium_summary(text):

    summary = summarize(text)

    return " ".join(

        summary.split()[:150]

    )


def long_summary(text):

    return summarize(text)


# ---------------------------------------------------------
# Compression Statistics
# ---------------------------------------------------------

def summary_statistics(
    original,
    summary
):

    original_words = len(original.split())

    summary_words = len(summary.split())

    compression = 0

    if original_words:

        compression = round(

            (
                1
                -
                summary_words /
                original_words
            ) * 100,

            2

        )

    return {

        "original_words": original_words,

        "summary_words": summary_words,

        "compression": compression

    }


# ---------------------------------------------------------
# Preview
# ---------------------------------------------------------

def preview_summary(
    summary,
    words=40
):

    tokens = summary.split()

    if len(tokens) <= words:

        return summary

    return " ".join(

        tokens[:words]

    ) + "..."