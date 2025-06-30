import numpy as np
from collections import defaultdict
from typing import List, Tuple, Callable, Optional
from aimakerspace.openai_utils.embedding import EmbeddingModel
import asyncio


def cosine_similarity(vector_a: np.array, vector_b: np.array) -> float:
    """Computes the cosine similarity between two vectors."""
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    return dot_product / (norm_a * norm_b)


def euclidean_distance(vector_a: np.array, vector_b: np.array) -> float:
    """Computes the Euclidean distance between two vectors."""
    return np.linalg.norm(vector_a - vector_b)


class VectorDatabase:
    def __init__(self, embedding_model: EmbeddingModel = None, is_pdf: bool = False):
        self.vectors = defaultdict(np.array)
        self.embedding_model = embedding_model or EmbeddingModel()
        self.metadata = defaultdict(dict)
        self.is_pdf = is_pdf

    def insert(self, key: str, vector: np.array) -> None:
        self.vectors[key] = vector

    def search(
        self,
        query_vector: np.array,
        k: int,
        distance_measure: Callable = cosine_similarity,
    ) -> List[Tuple[str, float]]:
        """
        Search for the top-k most similar vectors using the specified distance metric.
        If self.is_pdf is True, always use euclidean_distance.
        """
        metric = euclidean_distance if self.is_pdf else distance_measure
        scores = [
            (key, metric(query_vector, vector))
            for key, vector in self.vectors.items()
        ]
        return sorted(scores, key=lambda x: x[1], reverse=True)[:k]

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = cosine_similarity,
        return_as_text: bool = False,
    ) -> List[Tuple[str, float]]:
        """
        Search by text and return the top-k most similar vectors using the specified distance metric.
        If self.is_pdf is True, always use euclidean_distance.
        """
        metric = euclidean_distance if self.is_pdf else distance_measure
        query_vector = self.embedding_model.get_embedding(query_text)
        results = self.search(query_vector, k, metric)
        return [result[0] for result in results] if return_as_text else results

    def retrieve_from_key(self, key: str) -> np.array:
        return self.vectors.get(key, None)

    async def abuild_from_list(self, list_of_text: List[str]) -> "VectorDatabase":
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        for text, embedding in zip(list_of_text, embeddings):
            self.insert(text, np.array(embedding))
        return self

    def insert_with_metadata(self, key: str, vector: np.array, metadata: Optional[dict] = None) -> None:
        """
        Insert a vector with associated metadata.
        """
        self.vectors[key] = vector
        self.metadata[key] = metadata or {}

    def get_metadata(self, key: str) -> Optional[dict]:
        """
        Retrieve metadata for a given key.
        """
        return self.metadata.get(key)

    def update_metadata(self, key: str, metadata: dict) -> None:
        """
        Update metadata for a given key.
        """
        if key in self.vectors:
            self.metadata[key] = metadata

    def get_all_metadata(self) -> dict:
        """
        Retrieve the entire metadata dictionary.
        """
        return self.metadata

    def find_keys_by_metadata(self, metadata_filter: dict) -> list:
        """
        Return a list of keys whose metadata matches all items in metadata_filter.
        """
        return [
            key for key, meta in self.metadata.items()
            if all(item in meta.items() for item in metadata_filter.items())
        ]


if __name__ == "__main__":
    list_of_text = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]
    metadatas = [
        {"source": "doc1", "author": "John Doe"},
        {"source": "doc2", "author": "Jane Smith"},
        {"source": "doc3", "author": "John Doe"},
        {"source": "doc4", "author": "Jane Smith"},
        {"source": "doc5", "author": "John Doe"},
    ]

    # Example with is_pdf = False (default)
    vector_db = VectorDatabase()
    for text, metadata in zip(list_of_text, metadatas):
        embedding = vector_db.embedding_model.get_embedding(text)
        vector_db.insert_with_metadata(text, np.array(embedding), metadata)

    k = 2
    query_text = "I think fruit is awesome!"
    print("\n--- With is_pdf = False (default, uses cosine unless specified) ---")
    results_cosine = vector_db.search_by_text(query_text, k=k)
    print(f"Closest {k} vector(s) using default (cosine) distance:", results_cosine)
    from aimakerspace.vectordatabase import euclidean_distance
    results_euclid = vector_db.search_by_text(query_text, k=k, distance_measure=euclidean_distance)
    print(f"Closest {k} vector(s) using explicit Euclidean distance:", results_euclid)

    # Example with is_pdf = True (always uses Euclidean)
    vector_db_pdf = VectorDatabase(is_pdf=True)
    for text, metadata in zip(list_of_text, metadatas):
        embedding = vector_db_pdf.embedding_model.get_embedding(text)
        vector_db_pdf.insert_with_metadata(text, np.array(embedding), metadata)

    print("\n--- With is_pdf = True (always uses Euclidean distance) ---")
    results_pdf = vector_db_pdf.search_by_text(query_text, k=k)
    print(f"Closest {k} vector(s) with is_pdf=True (Euclidean):", results_pdf)

    # Retrieve metadata for a key
    print("Metadata for first key:", vector_db.get_metadata(list_of_text[0]))

    # Update metadata for a key
    vector_db.update_metadata(list_of_text[0], {"source": "doc1", "author": "Jane Smith", "updated": True})
    print("Updated metadata for first key:", vector_db.get_metadata(list_of_text[0]))

    # Get all metadata
    print("All metadata:", vector_db.get_all_metadata())

    # Find keys by metadata
    keys_by_author = vector_db.find_keys_by_metadata({"author": "John Doe"})
    print("Keys with author 'John Doe':", keys_by_author)

    # Retrieve vector by key
    retrieved_vector = vector_db.retrieve_from_key(list_of_text[0])
    print("Retrieved vector:", retrieved_vector)

    # Search by text and return only text
    relevant_texts = vector_db.search_by_text(
        "I think fruit is awesome!", k=k, return_as_text=True
    )
    print(f"Closest {k} text(s):", relevant_texts)
