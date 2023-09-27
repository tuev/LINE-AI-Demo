import pytest
from typing import List
from repository import llm_facade
from repository.vector_store_repo import VectorMetadata, VectorStoreRepo


def test_always_passes():
    assert True


test_store_namespace = "test-store"
test_document_name = "test-document"


def insert_sample_vectors(vector_store: VectorStoreRepo):
    texts = [
        "John and Jane are really enjoying their holiday in Greece.",
        "I recently started learning Python.",
        "Barcelona has a large and renowned university.",
        "Philosophy is a field of study that originated from Greek scholars.",
        "Mathematics is a difficult subject.",
    ]
    vector_embeddings: List[List[float]] = []
    vector_metadatas: List[VectorMetadata] = []
    for text in texts:
        vector_embeddings.append(llm_facade.openai_embeddings(text))
        vector_metadatas.append(VectorMetadata(content=text, page_number=None))

    vector_store.insert_vectors(
        test_store_namespace,
        test_document_name,
        vector_embeddings,
        metadatas=vector_metadatas,
    )


@pytest.fixture
def initialize_vector_store():
    vector_store = VectorStoreRepo("vector_store_test", 1536)
    insert_sample_vectors(vector_store)
    yield vector_store
    vector_store._drop_table()


def test_vector_store(initialize_vector_store):
    vector_store: VectorStoreRepo = initialize_vector_store

    if isinstance(vector_store, VectorStoreRepo) is False:
        raise Exception("failed initialize_vector_store")

    search_vector = llm_facade.openai_embeddings(
        "Athens is a beautiful city. I have been studying Math there for one year and I find it to be very challenging."  # noqa: E501
    )
    results = vector_store.similarity_search_by_namespace(
        search_vector, test_store_namespace
    )

    for result in results:
        print(result.metadata)

    expect_texts_order = [
        "Barcelona has a large and renowned university.",
        "John and Jane are really enjoying their holiday in Greece.",
        "Mathematics is a difficult subject.",
        "I recently started learning Python.",
        "Philosophy is a field of study that originated from Greek scholars.",
    ]

    # Assert desc order for similarity
    for i, result in enumerate(results):
        if i < len(results) - 2:
            assert result.similarity > results[i + 1].similarity

        assert result.metadata.content == expect_texts_order[i]
