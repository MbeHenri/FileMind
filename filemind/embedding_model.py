# from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
SPACE = "sbert"


class EmbeddingModel:

    def __init__(self, model: str, model_name: str = MODEL_NAME, space: str = SPACE):
        self.model_name = model_name
        self.space = space

        # self.model = SentenceTransformer(model_name)
        self.model = model

    def getDimension(self):
        return 3

    def encode(self, text: str, normalize_embeddings=True):
        return np.array([[0.3, 0.3, 0.3]])

    def embed_text(self, text: str) -> np.ndarray:
        # avec normalisation L2
        v = self.encode(text, normalize_embeddings=True)
        return v.astype("float32")
