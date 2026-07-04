"""Unit tests for embedding slice — cosine + get_embedding (mocked)."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from ollama_bench.features.embedding.command import TEST_PAIRS, cosine, get_embedding


def test_cosine_identical_vectors():
    v = [1.0, 2.0, 3.0]
    assert cosine(v, v) == 1.0


def test_cosine_orthogonal():
    assert cosine([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_cosine_opposite():
    assert cosine([1.0, 0.0], [-1.0, 0.0]) == -1.0


def test_cosine_empty():
    assert cosine([], []) == 0.0


def test_cosine_different_lengths():
    assert cosine([1.0, 2.0], [1.0]) == 0.0


def test_test_pairs_nonempty():
    assert len(TEST_PAIRS) >= 2
    for t1, t2 in TEST_PAIRS:
        assert isinstance(t1, str)
        assert isinstance(t2, str)


def test_get_embedding_parses_response():
    body = json.dumps({"embedding": [0.1, 0.2, 0.3]}).encode()
    mock = MagicMock()
    mock.__enter__.return_value.read.return_value = body
    with patch("urllib.request.urlopen", return_value=mock):
        r = get_embedding("nomic-embed-text", "hello")
    assert "err" not in r
    assert r["dim"] == 3
    assert r["embedding"] == [0.1, 0.2, 0.3]


def test_get_embedding_handles_error():
    with patch("urllib.request.urlopen", side_effect=Exception("net down")):
        r = get_embedding("m", "p")
    assert "err" in r
