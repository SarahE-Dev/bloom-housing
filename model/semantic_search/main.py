import logging
import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from rapidfuzz import process, fuzz

# Setup logging
def setup_logger():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)

logger = setup_logger()

# Base directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROVIDERS_PATH = os.path.join(BASE_DIR, "providers.json")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load providers on startup
try:
    with open(PROVIDERS_PATH, "r") as f:
        providers = json.load(f)
    logger.info("Providers data loaded successfully.")
except Exception as e:
    logger.critical(f"Failed to load providers: {e}")
    raise

# Prepare search dataset (you can match on provider names, services, or both)
provider_names = [provider["Provider"] for provider in providers]

@app.route("/search", methods=["POST"])
def search_endpoint():
    try:
        data = request.get_json(force=True)
        if "query" not in data:
            return jsonify({"error": "Missing query parameter"}), 400

        query = data["query"]
        top_n = int(data.get("top_n", 3))

        if top_n < 1 or top_n > len(providers):
            return jsonify({"error": f"top_n must be between 1 and {len(providers)}"}), 400

        # Use Rapidfuzz to get top matches
        matches = process.extract(
            query,
            provider_names,
            scorer=fuzz.WRatio,
            limit=top_n
        )

        results = []
        for match in matches:
            idx = match[2]  # Index in the original provider list
            results.append({
                "provider": providers[idx]["Provider"],
                "services": providers[idx]["Services"],
                "similarity_score": match[1] / 100  # Normalize to 0-1
            })

        return jsonify({"query": query, "results": results})

    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": "Search processing error"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
    logger.info(f"Starting Flask app on port {port}...")
