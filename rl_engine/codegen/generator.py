"""파싱된 게임 JSON → RL 환경 인스턴스 생성."""

from rl_engine.environments.economic_board.components import GameConfig
from rl_engine.environments.economic_board.template import EconomicBoardEnv


def create_environment(
    parsed_json: dict,
    num_players: int = 2,
    render_mode: str | None = None,
) -> EconomicBoardEnv:
    """
    파싱된 게임 JSON으로 RL 환경 인스턴스 생성.

    Args:
        parsed_json: 파싱된 게임 구조 JSON
        num_players: 플레이어 수
        render_mode: 렌더링 모드

    Returns:
        Gymnasium 환경 인스턴스
    """
    game_type = parsed_json.get("type", "economic_board")

    if game_type == "economic_board":
        config = GameConfig.from_parsed_json(parsed_json)
        num_players = max(config.num_players_min, min(num_players, config.num_players_max))
        return EconomicBoardEnv(
            game_config=config,
            num_players=num_players,
            render_mode=render_mode,
        )
    else:
        raise ValueError(f"Unsupported game type: {game_type}")


def generate_environment_code(parsed_json: dict) -> str:
    """
    파싱된 게임 JSON을 기반으로 환경 생성 Python 코드를 문자열로 반환.
    DB에 저장하거나 동적 실행 시 사용.
    """
    config = GameConfig.from_parsed_json(parsed_json)
    import json

    code = f'''"""Auto-generated RL environment for: {config.name}"""

import json
from rl_engine.environments.economic_board.components import GameConfig
from rl_engine.environments.economic_board.template import EconomicBoardEnv

GAME_JSON = {json.dumps(parsed_json, ensure_ascii=False, indent=2)}


def create_env(num_players: int = 2, render_mode: str | None = None) -> EconomicBoardEnv:
    config = GameConfig.from_parsed_json(GAME_JSON)
    num_players = max(config.num_players_min, min(num_players, config.num_players_max))
    return EconomicBoardEnv(game_config=config, num_players=num_players, render_mode=render_mode)


if __name__ == "__main__":
    env = create_env(render_mode="ansi")
    obs, info = env.reset()
    print(f"Environment created: {{config.name}}")
    print(f"Observation shape: {{obs.shape}}")
    print(f"Action space: {{env.action_space}}")
    print(f"Board: {{config.total_spaces}} spaces, {{len([s for s in config.spaces if s.is_buyable])}} buyable")
'''
    return code
