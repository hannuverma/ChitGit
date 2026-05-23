from qdrant_client import QdrantClient
from config.config import QDRANT_URL, QDRANT_API_KEY


client = QdrantClient(
    url=QDRANT_URL, 
    api_key=QDRANT_API_KEY,
    timeout=10,
    check_compatibility=False
)

# print(qdrant_client.get_collections())