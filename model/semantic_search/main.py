import json
import logging
import os
import threading

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def setup_logger():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


logger = setup_logger()

# Base directory and file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROVIDERS_PATH = os.path.join(BASE_DIR, "providers.json")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings.npy")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# A lock to prevent race conditions when reading/writing data files
data_lock = threading.Lock()


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
    try:
        data = request.get_json(force=True)

        if "query" not in data:
            return jsonify({"error": "Missing query parameter"}), 400

        query = data["query"]
        top_n = int(data.get("top_n", 3))

        # We use the global providers list loaded at startup
        if top_n < 1 or top_n > len(providers):
            return (
                jsonify({"error": f"top_n must be between 1 and {len(providers)}"}),
                400,
            )

        # Generate query embedding
        query_embedding = model.encode([query])

        # Calculate similarities against in-memory embeddings
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


# Update resources and refresh in-memory data without restarting the app
@app.route("/update", methods=["POST"])
def add_provider_endpoint():
    # Enable write to global variables
    global providers, embeddings

    try:
        data = request.get_json(force=True)
        new_provider = data.get("Provider")
        new_services = data.get("Services")

        if not new_provider or not new_services:
            return jsonify({"error": "Missing 'provider' or 'services' parameter"}), 400

        new_provider_obj = {"Provider": new_provider, "Services": new_services}

        # Generate embedding for the new provider
        logger.info(f"Generating embedding for new provider: {new_provider}")
        new_text = f"{new_provider_obj['Provider']}. {new_provider_obj['Services']}"
        new_embedding = model.encode([new_text])  # Shape: (1, 384)

        # use lock context manager to ensure thread safety
        with data_lock:
            logger.info("Acquired lock to update data files and in-memory state.")

            # use the 'providers' global which is already a list of dicts
            updated_providers = providers + [new_provider_obj]
            with open(PROVIDERS_PATH, "w") as f:
                json.dump(updated_providers, f, indent=4)
            logger.info(f"Successfully updated {PROVIDERS_PATH}")

            # use the 'embeddings' global which is already a numpy array
            updated_embeddings = np.vstack([embeddings, new_embedding])
            np.save(EMBEDDINGS_PATH, updated_embeddings)
            logger.info(
                f"Successfully updated {EMBEDDINGS_PATH} with new shape {updated_embeddings.shape}"
            )

            providers = updated_providers
            embeddings = updated_embeddings

            logger.info("Released lock. In-memory data is now current.")

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Provider added and embeddings updated.",
                    "new_provider": new_provider_obj,
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error adding provider: {e}")
        return jsonify({"error": "Error processing your request"}), 500


if __name__ == "__main__":
    # Load the model and initial data when the application starts
    try:
        model, providers, embeddings = load_model_and_data()
    except Exception as e:
        logger.critical(f"Application startup failed: {e}")
        exit(1)

    port = int(os.getenv("PORT", 5001))
    logger.info(f"Starting Flask app on port {port}...")
    app.run(host="0.0.0.0", port=port)
