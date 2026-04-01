"""
게임 레퍼런스 시드 데이터를 Supabase에 삽입하는 스크립트.
임베딩은 sentence-transformers의 all-MiniLM-L6-v2 모델로 생성 (384차원).

Usage:
    cd boardgame-tester
    python data/scripts/seed_references.py
"""

import json
import os
import sys

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client

load_dotenv()


def main():
    # Supabase 클라이언트
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)

    # 시드 데이터 로드
    seed_path = os.path.join(os.path.dirname(__file__), "..", "raw", "board_games", "seed_data.json")
    with open(seed_path, "r", encoding="utf-8") as f:
        games = json.load(f)

    print(f"Loaded {len(games)} games from seed data")

    # 임베딩 모델 로드
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # 기존 데이터 확인
    existing = supabase.table("game_references").select("name").execute()
    existing_names = {r["name"] for r in existing.data}

    inserted = 0
    skipped = 0

    for game in games:
        if game["name"] in existing_names:
            print(f"  Skipping (already exists): {game['name']}")
            skipped += 1
            continue

        # 임베딩 생성 (규칙 요약 기반)
        embedding_text = f"{game['name']}: {game['rules_summary']}"
        embedding = model.encode(embedding_text).tolist()

        # Supabase에 삽입
        record = {
            "name": game["name"],
            "genre": game["genre"],
            "rules_summary": game["rules_summary"],
            "balance_data": game["balance_data"],
            "strategies": game["strategies"],
            "embedding": embedding,
            "source": game.get("source", ""),
        }

        supabase.table("game_references").insert(record).execute()
        print(f"  Inserted: {game['name']}")
        inserted += 1

    print(f"\nDone! Inserted: {inserted}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
