
import faiss
import numpy as np
import json
import os
import pickle
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class IndexManager:
    def __init__(self, use_persistent=True):
        self.dimension = 512 # CLIP ViT-B/16 output dim
        self.index = None
        self.metadata = []
        self.use_persistent = use_persistent
        
        if self.use_persistent:
            self.load_index()
        else:
            self.reset_index()

    def reset_index(self):
        """Create a fresh index (for session mode or rebuild)."""
        self.index = faiss.IndexFlatIP(self.dimension) # Inner Product for cosine sim (normalized vectors)
        self.metadata = []

    def load_index(self):
        """Load persistent index if exists."""
        if os.path.exists(config.CCTV_INDEX_PATH) and os.path.exists(config.CCTV_META_PATH):
            try:
                self.index = faiss.read_index(config.CCTV_INDEX_PATH)
                with open(config.CCTV_META_PATH, 'r') as f:
                    self.metadata = json.load(f)
                print(f"Loaded persistent index with {self.index.ntotal} vectors.")
            except Exception as e:
                print(f"Failed to load index: {e}. Starting fresh.")
                self.reset_index()
        else:
            self.reset_index()

    def save_index(self):
        """Save index to disk (only in persistent mode)."""
        if not self.use_persistent: return
        
        faiss.write_index(self.index, config.CCTV_INDEX_PATH)
        with open(config.CCTV_META_PATH, 'w') as f:
            json.dump(self.metadata, f)
        print("Index saved to disk.")

    def add_items(self, embeddings, meta_list):
        """
        Add batch of embeddings and metadata.
        embeddings: numpy array (N, 512)
        meta_list: list of dicts
        """
        if len(embeddings) == 0: return
        
        faiss.normalize_L2(embeddings) # Ensure normalized for Cosine Similarity via IP
        self.index.add(embeddings)
        self.metadata.extend(meta_list)

    def search(self, query_vector, top_k=50):
        """
        Search the index.
        query_vector: numpy array (1, 512)
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                item = self.metadata[idx].copy()
                item['score'] = float(distances[0][i])
                results.append(item)
        
        return results
