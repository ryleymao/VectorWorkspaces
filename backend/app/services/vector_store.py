import faiss
import numpy as np
import os
from typing import List
from app.core.config import settings
from app.core.logger import logger


class VectorStore:
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
        os.makedirs(settings.FAISS_STORAGE_PATH, exist_ok=True)
        self.index_path = os.path.join(settings.FAISS_STORAGE_PATH, f"{tenant_id}.index")
        self.index = None
        self.dimension = 384
    
    def load_index(self):
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                logger.info(f"Loaded FAISS index for tenant {self.tenant_id}")
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
                self._create_index()
        else:
            self._create_index()
        return self.index
    
    def _create_index(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info(f"Created new FAISS index for tenant {self.tenant_id}")
    
    def add_vectors(self, vectors: np.ndarray, ids: np.ndarray = None):
        if self.index is None:
            self.load_index()
        
        if ids is not None and len(ids) > 0:
            if isinstance(self.index, faiss.IndexIDMap):
                self.index.add_with_ids(vectors.astype('float32'), ids.astype('int64'))
            else:
                id_map = faiss.IndexIDMap(self.index)
                id_map.add_with_ids(vectors.astype('float32'), ids.astype('int64'))
                self.index = id_map
        else:
            self.index.add(vectors.astype('float32'))
        
        self._save_index()
    
    def search(self, query_vector: np.ndarray, k: int = 5):
        if self.index is None:
            self.load_index()
        
        if self.index.ntotal == 0:
            return np.array([]), np.array([])
        
        query_vector = query_vector.reshape(1, -1).astype('float32')
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_vector, k)
        return distances[0], indices[0]
    
    def _save_index(self):
        faiss.write_index(self.index, self.index_path)
        logger.info(f"Saved FAISS index for tenant {self.tenant_id}")
