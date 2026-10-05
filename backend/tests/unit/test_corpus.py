import pytest
from research.datasets.corpus.data import get_corpus, RAW_DOCUMENTS, get_deterministic_uuid


def test_corpus_total_document_count():
    """
    Test 1: Corpus contains exactly 48 documents.
    """
    corpus = get_corpus()
    assert len(corpus) == 48
    assert len(RAW_DOCUMENTS) == 48


def test_corpus_department_distribution():
    """
    Test 2: Each of the 4 departments contains exactly 12 documents.
    """
    corpus = get_corpus()
    departments = [doc["department"] for doc in corpus]
    
    assert departments.count("hr") == 12
    assert departments.count("finance") == 12
    assert departments.count("engineering") == 12
    assert departments.count("legal") == 12


def test_corpus_required_metadata_presence():
    """
    Test 3: Every document contains all required metadata attributes.
    """
    required_fields = [
        "id",
        "doc_key",
        "title",
        "filename",
        "department",
        "classification",
        "clearance_level",
        "source_type",
        "issuing_department",
        "author_role",
        "source_authority",
        "trust_status",
        "content",
    ]
    corpus = get_corpus()
    for doc in corpus:
        for field in required_fields:
            assert field in doc, f"Document {doc.get('doc_key')} missing '{field}'"
            assert doc[field] is not None, f"Document {doc.get('doc_key')} has None for '{field}'"
            if isinstance(doc[field], str):
                assert len(doc[field].strip()) > 0, f"Document {doc.get('doc_key')} has empty '{field}'"


def test_corpus_classification_and_clearance_validity():
    """
    Test 4: Classification values are valid and align strictly with numeric clearance levels.
    """
    valid_classifications = {"public": 1, "internal": 2, "confidential": 3, "restricted": 4}
    corpus = get_corpus()

    for doc in corpus:
        classification = doc["classification"]
        clearance = doc["clearance_level"]

        assert classification in valid_classifications, f"Invalid classification '{classification}' in {doc['doc_key']}"
        assert clearance == valid_classifications[classification], (
            f"Clearance level {clearance} does not match classification '{classification}' in {doc['doc_key']}"
        )


def test_corpus_deterministic_uuids():
    """
    Test: Document UUID generation is 100% deterministic and unique.
    """
    corpus_1 = get_corpus()
    corpus_2 = get_corpus()

    ids_1 = [str(doc["id"]) for doc in corpus_1]
    ids_2 = [str(doc["id"]) for doc in corpus_2]

    assert ids_1 == ids_2
    assert len(set(ids_1)) == 48, "Duplicate document UUIDs found in corpus"
