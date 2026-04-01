"""pgvector 기반 유사 게임 검색."""

from supabase import Client
from ai_pipeline.rag.embedder import embed_text


def search_similar_games(
    query_text: str,
    supabase: Client,
    genre: str = "economic_board",
    top_k: int = 3,
) -> list[dict]:
    """
    규칙 텍스트와 유사한 기존 게임을 벡터 검색.

    Args:
        query_text: 검색할 규칙 텍스트 (또는 게임 설명)
        supabase: Supabase 클라이언트
        genre: 필터링할 장르
        top_k: 반환할 결과 수

    Returns:
        유사 게임 레퍼런스 목록 (similarity 높은 순)
    """
    query_embedding = embed_text(query_text)

    # Supabase RPC로 벡터 유사도 검색
    result = supabase.rpc(
        "match_game_references",
        {
            "query_embedding": query_embedding,
            "match_genre": genre,
            "match_count": top_k,
        },
    ).execute()

    return result.data


def get_all_references(
    supabase: Client,
    genre: str | None = None,
) -> list[dict]:
    """장르별 또는 전체 게임 레퍼런스 조회."""
    query = supabase.table("game_references").select(
        "id, name, genre, rules_summary, balance_data, strategies, source"
    )
    if genre:
        query = query.eq("genre", genre)

    result = query.execute()
    return result.data
