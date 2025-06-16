# app.py
import os
import time
import logging
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS

import tensorflow as tf
import google.generativeai as genai
from langchain_community.embeddings import TensorflowHubEmbeddings
from langchain_community.vectorstores import Chroma

# ─── Setup & Configuration ─────────────────────────────────────────────────────

# Force TensorFlow to CPU only
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
tf.config.set_visible_devices([], 'GPU')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Google API Configuration
GOOGLE_API_KEY=your_api_key_here

# Optional Configuration
TEMPERATURE=0.1
MAX_OUTPUT_TOKENS=1024
TOP_K_DOCUMENTS=5

genai.configure(api_key=GOOGLE_API_KEY)

# Constants
CHROMA_DIR       = Path("./chroma_db")
COLLECTION_NAME  = "rag_collection"
EMBED_MODEL_URL  = "https://tfhub.dev/google/universal-sentence-encoder-large/5"
TOP_K            = 5
AI_MODEL_NAME    = "gemini-1.5-flash"

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# ─── RAG Setup ──────────────────────────────────────────────────────────────────

def initialize_retriever():
    """Load or create Chroma DB retriever with TF‑Hub embeddings."""
    embed_fn = TensorflowHubEmbeddings(model_url=EMBED_MODEL_URL)
    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=embed_fn
    )
    return db.as_retriever(search_kwargs={"k": TOP_K})

retriever = initialize_retriever()
model     = genai.GenerativeModel(AI_MODEL_NAME)

# ─── Helper Functions ──────────────────────────────────────────────────────────

def create_prompt(query: str, docs: list) -> str:
    """Build system prompt injecting retrieved document contexts."""
    parts = []
    for i, doc in enumerate(docs, start=1):
        src = doc.metadata.get("source", "Unknown")
        content = doc.page_content.strip().replace("\n", " ")
        parts.append(f"[Doc {i} – {src}]\n{content[:800]}")
    context = "\n\n".join(parts)

    return (
        "You are a helpful assistant. Answer using ONLY the context below.\n\n"
        f"{context}\n\n"
        f"Question: {query}\n\n"
        "If the answer is not in the context, say so clearly.\n"
        "Cite document numbers where you pull your facts.\n\n"
        "Answer:"
    )

def get_ai_response(prompt: str) -> str:
    """Call Google Generative AI with light rate‑limiting."""
    time.sleep(0.1)
    resp = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,
            top_p=0.8,
            top_k=40,
            max_output_tokens=1024,
        )
    )
    return resp.text or "No response generated."

def format_sources(docs: list) -> list:
    """Return a simple list of source strings for the client."""
    out = []
    for i, doc in enumerate(docs, start=1):
        md = doc.metadata
        info = md.get("source", "Unknown")
        if "page" in md:
            info += f" (page {md['page']})"
        out.append(f"Doc {i}: {info}")
    return out

# ─── Flask Routes ──────────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    query = data.get("query", "").strip()
    if not query:
        return jsonify(error="`query` field is required"), 400

    docs = retriever.get_relevant_documents(query)
    if not docs:
        return jsonify(answer="No relevant documents found.", sources=[])

    prompt    = create_prompt(query, docs)
    answer    = get_ai_response(prompt)
    sources   = format_sources(docs)

    return jsonify(answer=answer, sources=sources)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(status="healthy")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

