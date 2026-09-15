import os

import numpy as np


def _encode(guide):
    return np.array([guide.count(base) / len(guide) for base in "ACGT"], dtype="float32")


def vector_search(state):
    ranked_guides = state.get("ranked_guides", [])
    if not ranked_guides:
        return {"similar_guides": [], "vector_search_mode": "disabled"}

    query = _encode(ranked_guides[0]["guide"])
    matrix = np.vstack([_encode(item["guide"]) for item in ranked_guides])
    distances = np.linalg.norm(matrix - query, axis=1)
    order = np.argsort(distances)[:5]
    mode = "numpy_fallback"

    if os.getenv("BIOGRAPH_VECTOR_BACKEND", "").lower() == "faiss":
        try:
            import faiss

            index = faiss.IndexFlatL2(matrix.shape[1])
            index.add(matrix)
            distances, indices = index.search(query.reshape(1, -1), min(5, len(matrix)))
            order = indices[0]
            distances = distances[0]
            mode = "faiss"
        except ImportError:
            pass

    return {
        "similar_guides": [
            {
                "guide": ranked_guides[index]["guide"],
                "distance": round(float(distances[position]), 4),
            }
            for position, index in enumerate(order)
        ],
        "vector_search_mode": mode,
    }
