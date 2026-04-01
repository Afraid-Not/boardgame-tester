"""텍스트 → 벡터 임베딩 생성."""

from sentence_transformers import SentenceTransformer

_model = None


def get_model() -> SentenceTransformer:
    """싱글톤 임베딩 모델 반환."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text: str) -> list[float]:
    """텍스트를 384차원 벡터로 변환."""
    model = get_model()
    return model.encode(text).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """여러 텍스트를 벡터로 일괄 변환."""
    model = get_model()
    return model.encode(texts).tolist()
