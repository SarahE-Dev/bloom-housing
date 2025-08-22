import json
import logging
import os

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


# Setup logging
def setup_logger():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


logger = setup_logger()

# Base directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROVIDERS_PATH = os.path.join(BASE_DIR, "providers.json")  # Path to saved providers

# Initialize Flask app
app = Flask(__name__)
CORS(app)
MODEL_NAME = "all-MiniLM-L6-v2"
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
COLLECTION_NAME = "service_providers"


# Load model and create embeddings on startup
def load_model_and_client():
    try:
        logger.info(f"Loading sentence transformer model: {MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)

        logger.info(f"Connecting to Qdrant at {QDRANT_HOST}")
        client = QdrantClient(host=QDRANT_HOST, port=6333)

        return model, client
    except Exception as e:
        logger.critical(f"Failed to load model or connect to QDRANT: {e}")
        raise


# Load model and embeddings on startup
try:
    model, client = load_model_and_client()  # Modified to load providers as well
except Exception as e:
    logger.critical(f"Application startup failed: {e}")
    raise


@app.route("/search", methods=["POST"])
def search_endpoint():
    try:
        data = request.get_json(force=True)

        if "query" not in data:
            return jsonify({"error": "Missing query parameter"}), 400

        query = data["query"]
        top_n = int(data.get("top_n", 3))

        # Validate top_n
        if top_n < 1:
            return jsonify({"error": "top_n must be at least 1"}), 400

        # Generate query embedding
        query_embedding = model.encode([query])

        # Search in Qdrant
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding[0],
            limit=top_n,
        )

        # Format results
        results = []
        for hit in search_result:
            results.append(
                {
                    "provider": hit.payload["Provider"],
                    "services": hit.payload["Services"],
                    "similarity_score": float(hit.score),
                }
            )

        return jsonify({"query": query, "results": results})

    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": "Search processing error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
    logger.info(f"Starting Flask app on port {port}...")
