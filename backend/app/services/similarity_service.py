from sentence_transformers import SentenceTransformer, util


class SimilarityService:
    def __init__(self):
        """
        Load the embedding model once when the service is created.
        """
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def compute_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Compute semantic similarity between two texts.

        Returns a score between 0 and 1.
        """

        # Convert both texts into embeddings
        embedding1 = self.model.encode(
            text1,
            convert_to_tensor=True
        )
        embedding2 = self.model.encode(
            text2,
            convert_to_tensor=True
        )

        # Cosine similarity
        similarity = util.cos_sim(
            embedding1,
            embedding2
        )

        # Convert tensor result to Python float
        return float(similarity.item())