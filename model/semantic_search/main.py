import json
import logging
import os
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


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
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings.npy")  # Path to saved embeddings

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load model and create embeddings on startup
def load_model_and_data():
    model_name = "all-MiniLM-L6-v2"
    try:
        logger.info(f"Loading sentence transformer model: {model_name}")
        model = SentenceTransformer(model_name)

        logger.info(f"Loading providers data from {PROVIDERS_PATH}...")
        with open(PROVIDERS_PATH, "r") as f:
            providers = json.load(f)
        logger.info("Providers data loaded.")

        logger.info(f"Loading embeddings from {EMBEDDINGS_PATH}...")
        embeddings = np.load(EMBEDDINGS_PATH)
        logger.info(f"Successfully loaded embeddings with shape: {embeddings.shape}")

        return model, providers, embeddings
    except FileNotFoundError:
        logger.critical(f"Data files not found. Please run prepare_data.py first.")
        raise
    except Exception as e:
        logger.critical(f"Failed to load model or data: {e}")
        raise


# Load model and embeddings on startup
try:
    model, providers, embeddings = (
        load_model_and_data()
    )  # Modified to load providers as well
except Exception as e:
    logger.critical(f"Application startup failed: {e}")
    raise


@app.route("/search", methods=["POST"])
def search_endpoint():
    """Search endpoint"""
    try:
        data = request.get_json(force=True)

        if "query" not in data:
            return jsonify({"error": "Missing query parameter"}), 400

        query = data["query"]
        top_n = int(data.get("top_n", 3))

        # Validate top_n
        if top_n < 1 or top_n > len(providers):
            return (
                jsonify({"error": f"top_n must be between 1 and {len(providers)}"}),
                400,
            )

        # Generate query embedding
        query_embedding = model.encode([query])

        # Calculate similarities
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:top_n]

        # Format results
        results = []
        for i in top_indices:
            results.append(
                {
                    "provider": providers[i]["Provider"],
                    "services": providers[i]["Services"],
                    "similarity_score": float(similarities[i]),
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
