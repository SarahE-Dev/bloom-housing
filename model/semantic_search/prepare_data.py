import json
import logging
import os

import numpy as np
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import VectorParams
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Base DIR, Provider, model and QDRANT + Collection info
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROVIDERS_PATH = os.path.join(BASE_DIR, "providers.json")
MODEL_NAME = "all-MiniLM-L6-v2"
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
COLLECTION_NAME = "service_providers"


def generate_and_save_data():
    # Initialize client
    logger.info(f"Qdrant client connected to {QDRANT_HOST}")
    client = QdrantClient(host=QDRANT_HOST, port=6333)

    logger.info(f"Loading Sentence Transformers model... {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    try:
        if client.get_collection(collection_name=COLLECTION_NAME):
            logger.info(f"Collection {COLLECTION_NAME} already exists.")
            client.delete_collection(collection_name=COLLECTION_NAME)
    except Exception:
        logger.info(
            f"Collection {COLLECTION_NAME} does not exist. Creating new collection."
        )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=model.get_sentence_embedding_dimension(), distance="Cosine"
        ),
    )

    logger.info(f"Collection {COLLECTION_NAME} created.")
    logger.info(f"Loading provider information from {PROVIDERS_PATH}")

    with open("providers.json", "r") as f:
        providers = json.load(f)

    services = [f"{entry['Services']}" for entry in providers]
    embeddings = model.encode(services, show_progress_bar=True)

    logger.info("Uploading vectors to Qdrant...")
    for idx, (provider, embedding) in enumerate(zip(providers, embeddings)):
        logger.info(f"Processing provider: {provider['Provider']}")
        points = [
            models.PointStruct(id=idx, vector=embedding.tolist(), payload=provider)
        ]

    client.upload_points(collection_name=COLLECTION_NAME, points=points, wait=True)

    logger.info("Data upload complete.")


if __name__ == "__main__":
    logger.info("Starting data preparation process...")
    generate_and_save_data()
