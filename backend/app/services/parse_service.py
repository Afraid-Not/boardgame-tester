"""규칙 파싱 서비스. Claude API 파싱 + RAG + 환경 코드 생성을 오케스트레이션."""

import json
import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from app.config import get_settings
from app.db.client import get_supabase

from ai_pipeline.parsing.text_parser import parse_rules_text
from ai_pipeline.parsing.image_parser import parse_rules_image
from ai_pipeline.rag.retriever import search_similar_games
from rl_engine.codegen.generator import generate_environment_code
from rl_engine.codegen.validator import validate_environment


async def parse_game_rules(
    game_id: str,
    rules_text: str | None = None,
    image_data: bytes | None = None,
    media_type: str | None = None,
) -> dict:
    """
    게임 규칙을 파싱하고, 환경 코드를 생성/검증하여 DB에 저장.

    Returns:
        {"parsed_structure": dict, "environment_code": str, "validation": dict}
    """
    settings = get_settings()
    supabase = get_supabase()

    # 1. 상태를 parsing으로 업데이트
    supabase.table("games").update({"status": "parsing"}).eq("id", game_id).execute()

    try:
        # 2. RAG: 유사 게임 검색
        search_query = rules_text[:500] if rules_text else "economic board game"
        rag_refs = search_similar_games(
            query_text=search_query,
            supabase=supabase,
            genre="economic_board",
            top_k=3,
        )

        # 3. 규칙 파싱
        if image_data and media_type:
            parsed = parse_rules_image(
                image_data=image_data,
                media_type=media_type,
                api_key=settings.openai_api_key,
                rag_references=rag_refs,
            )
        elif rules_text:
            parsed = parse_rules_text(
                rules_text=rules_text,
                api_key=settings.openai_api_key,
                rag_references=rag_refs,
            )
        else:
            raise ValueError("Either rules_text or image_data must be provided")

        # 4. RL 환경 코드 생성
        env_code = generate_environment_code(parsed)

        # 5. 환경 검증
        validation = validate_environment(parsed, num_steps=50)

        # 6. DB 저장
        status = "ready" if validation["valid"] else "parsing"
        supabase.table("games").update({
            "rules_text": rules_text or "(parsed from image)",
            "parsed_structure": parsed,
            "environment_code": env_code,
            "status": status,
        }).eq("id", game_id).execute()

        return {
            "parsed_structure": parsed,
            "environment_code": env_code,
            "validation": validation,
        }

    except Exception as e:
        # 실패 시 에러 정보 저장
        supabase.table("games").update({
            "status": "parsing",
            "parsed_structure": {"error": str(e)},
        }).eq("id", game_id).execute()
        raise
