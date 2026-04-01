from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import Optional
from app.models.game import GameCreate, GameResponse, GameGenre
from app.db.client import get_supabase
from app.services.parse_service import parse_game_rules

router = APIRouter(prefix="/api/games", tags=["games"])


@router.post("", response_model=GameResponse)
async def create_game(game: GameCreate):
    supabase = get_supabase()
    result = supabase.table("games").insert({
        "name": game.name,
        "genre": game.genre.value,
    }).execute()
    return result.data[0]


@router.get("", response_model=list[GameResponse])
async def list_games():
    supabase = get_supabase()
    result = supabase.table("games").select("*").order("created_at", desc=True).execute()
    return result.data


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(game_id: str):
    supabase = get_supabase()
    result = supabase.table("games").select("*").eq("id", game_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Game not found")
    return result.data[0]


@router.post("/{game_id}/parse")
async def parse_game(
    game_id: str,
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    rules_text: Optional[str] = Form(None),
):
    if not file and not rules_text:
        raise HTTPException(status_code=400, detail="Either file or rules_text is required")

    # 게임 존재 확인
    supabase = get_supabase()
    game = supabase.table("games").select("id").eq("id", game_id).execute()
    if not game.data:
        raise HTTPException(status_code=404, detail="Game not found")

    # 이미지/파일 처리
    image_data = None
    media_type = None
    if file:
        image_data = await file.read()
        media_type = file.content_type

    # 백그라운드에서 파싱 실행
    background_tasks.add_task(
        parse_game_rules,
        game_id=game_id,
        rules_text=rules_text,
        image_data=image_data,
        media_type=media_type,
    )

    return {"message": "Parsing started", "game_id": game_id}


@router.get("/{game_id}/environment")
async def get_environment(game_id: str):
    supabase = get_supabase()
    result = supabase.table("games").select("environment_code").eq("id", game_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Game not found")
    if not result.data[0].get("environment_code"):
        raise HTTPException(status_code=404, detail="Environment code not generated yet")
    return {"environment_code": result.data[0]["environment_code"]}
