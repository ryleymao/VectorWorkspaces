from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL
    
    def load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
        return self.model
    
    def embed_text(self, text: str) -> np.ndarray:
        model = self.load_model()
        return model.encode(text, convert_to_numpy=True)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        model = self.load_model()
        return model.encode(texts, convert_to_numpy=True)


embedding_service = EmbeddingService()

