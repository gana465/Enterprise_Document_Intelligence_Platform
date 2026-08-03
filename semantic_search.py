"""
semantic_search.py
-------------------------------------------------
Semantic Search Engine
Enterprise Document Intelligence Platform
-------------------------------------------------
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    EMBEDDING_FOLDER,
    EMBEDDING_MODEL,
    TOP_K_RESULTS
)

# -------------------------------------------------------
# Load Embedding Model (Singleton)
# -------------------------------------------------------

_model = None


def get_model() -> SentenceTransformer:
    """
    Load the embedding model only once.
    """

    global _model

    if _model is None:

        _model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    return _model


# -------------------------------------------------------
# Create Embedding
# -------------------------------------------------------

def create_embedding(text: str):

    if not text.strip():
        return None

    model = get_model()

    vector = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return vector.astype(np.float32)


# -------------------------------------------------------
# Embedding Path
# -------------------------------------------------------

def embedding_path(document_id: int):

    return EMBEDDING_FOLDER / f"{document_id}.pkl"


# -------------------------------------------------------
# Save Embedding
# -------------------------------------------------------

def save_embedding(document_id: int, embedding):

    with open(
        embedding_path(document_id),
        "wb"
    ) as f:

        pickle.dump(
            embedding,
            f
        )


# -------------------------------------------------------
# Load Embedding
# -------------------------------------------------------

def load_embedding(document_id: int):

    path = embedding_path(document_id)

    if not path.exists():

        return None

    with open(path, "rb") as f:

        return pickle.load(f)

# -------------------------------------------------------
# Embedding File Path
# -------------------------------------------------------

from pathlib import Path
import pickle

from config import EMBEDDINGS_DIR


def embedding_path(document_id: int) -> Path:
    """
    Returns the embedding file path for a document.
    """
    return Path(EMBEDDINGS_DIR) / f"{document_id}.pkl"


# -------------------------------------------------------
# Save Embedding
# -------------------------------------------------------

def save_embedding(document_id: int, embedding):

    path = embedding_path(document_id)

    with open(path, "wb") as f:
        pickle.dump(embedding, f)


# -------------------------------------------------------
# Load Embedding
# -------------------------------------------------------

def load_embedding(document_id: int):

    path = embedding_path(document_id)

    if not path.exists():
        return None

    with open(path, "rb") as f:
        return pickle.load(f)


# -------------------------------------------------------
# Delete Embedding
# -------------------------------------------------------

def delete_embedding(document_id: int):

    path = embedding_path(document_id)

    if path.exists():
        path.unlink()

    return True


# -------------------------------------------------------
# Check Embedding
# -------------------------------------------------------

def embedding_exists(document_id: int):

    return embedding_path(document_id).exists()
# -------------------------------------------------------
# Delete Embedding
# -------------------------------------------------------

def delete_embedding(document_id: int):

    path = embedding_path(document_id)

    if path.exists():

        path.unlink()


# -------------------------------------------------------
# Generate + Save
# -------------------------------------------------------

def build_document_embedding(
    document_id: int,
    text: str
):

    embedding = create_embedding(text)

    if embedding is None:

        return False

    save_embedding(
        document_id,
        embedding
    )

    return True


# -------------------------------------------------------
# Batch Generation
# -------------------------------------------------------

def build_all_embeddings(
    documents: Iterable
):

    for doc in documents:

        if not doc.extracted_text:

            continue

        build_document_embedding(
            doc.id,
            doc.extracted_text
        )


# -------------------------------------------------------
# Similarity
# -------------------------------------------------------

def similarity(
    emb1,
    emb2
):

    score = cosine_similarity(
        [emb1],
        [emb2]
    )[0][0]

    return float(score)


# -------------------------------------------------------
# Semantic Search
# -------------------------------------------------------

def semantic_search(query, documents, top_k=5):

    query_embedding = create_embedding(query)

    if query_embedding is None:

        return []

    results = []

    for doc in documents:

        emb = load_embedding(doc.id)

        if emb is None:

            continue

        score = similarity(
            query_embedding,
            emb
        )

        results.append(
            {
                "document_id": doc.id,
                "document": doc,
                "score": score
            })
    results.sort(

        key=lambda x: x["score"],

        reverse=True

    )

    return results[:top_k]


# -------------------------------------------------------
# Similar Documents
# -------------------------------------------------------

def similar_documents(
    document_id,
    documents,
    top_k=5
):

    source = load_embedding(document_id)

    if source is None:

        return []

    results = []

    for doc in documents:

        if doc.id == document_id:

            continue

        emb = load_embedding(doc.id)

        if emb is None:

            continue

        score = similarity(
            source,
            emb
        )

        results.append(

            (

                doc,

                score

            )

        )

    results.sort(

        key=lambda x: x[1],

        reverse=True

    )

    return results[:top_k]


# -------------------------------------------------------
# Refresh Embedding
# -------------------------------------------------------

def refresh_embedding(
    document
):

    build_document_embedding(

        document.id,

        document.extracted_text

    )


# -------------------------------------------------------
# Embedding Exists
# -------------------------------------------------------

def embedding_exists(
    document_id
):

    return embedding_path(
        document_id
    ).exists()