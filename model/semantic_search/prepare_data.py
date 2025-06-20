import json
import logging
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Base directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_and_save_data():
    model_name = "all-MiniLM-L6-v2"
    output_providers_path = os.path.join(BASE_DIR, "providers.json")
    output_embeddings_path = os.path.join(BASE_DIR, "embeddings.npy")

    try:
        logger.info(f"Loading providers data from {output_providers_path}...")
        with open(output_providers_path, "r") as f:
            providers = json.load(f)

        logger.info(f"Loading sentence transformer model: {model_name}")
        model = SentenceTransformer(model_name)

        logger.info("Creating service embeddings...")
        texts = [f"{entry['Provider']}. {entry['Services']}" for entry in providers]
        embeddings = model.encode(texts, show_progress_bar=True)

        logger.info(f"Successfully created embeddings with shape: {embeddings.shape}")

        logger.info(f"Saving providers data to {output_providers_path}...")
        with open(output_providers_path, "w") as f:
            json.dump(providers, f, indent=4)
        logger.info("Providers data saved.")

        logger.info(f"Saving embeddings to {output_embeddings_path}...")
        np.save(output_embeddings_path, embeddings)
        logger.info("Embeddings saved.")

    except Exception as e:
        logger.critical(f"Failed during data preparation: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting data preparation process...")
    generate_and_save_data()
    logger.info("Data preparation process completed.")
