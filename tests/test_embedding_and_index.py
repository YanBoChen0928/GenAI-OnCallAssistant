import numpy as np
from annoy import AnnoyIndex
import pytest
from data_processing import DataProcessor

@pytest.fixture(scope="module")
def processor():
    return DataProcessor(base_dir=".")

def test_embedding_dimensions(processor):
    # load emergency embeddings
    emb = np.load(processor.models_dir / "embeddings" / "emergency_embeddings.npy")
    expected_dim = processor.embedding_dim
    assert emb.ndim == 2, f"Expected 2D array, got {emb.ndim}D"
    assert emb.shape[1] == expected_dim, (
        f"Expected embedding dimension {expected_dim}, got {emb.shape[1]}"
    )

def test_annoy_search(processor):
    # load embeddings
    emb = np.load(processor.models_dir / "embeddings" / "emergency_embeddings.npy")
    # load Annoy index
    idx = AnnoyIndex(processor.embedding_dim, 'angular')
    idx.load(str(processor.models_dir / "indices" / "annoy" / "emergency_index.ann"))
    # perform a sample query
    query_vec = emb[0]
    ids, distances = idx.get_nns_by_vector(query_vec, 5, include_distances=True)
    assert len(ids) == 5
    assert all(0 <= d <= 2 for d in distances)
