"""학습된 모델 평가. N판 대전 결과 통계 수집."""

import numpy as np
from collections import defaultdict

from rl_engine.codegen.generator import create_environment
from rl_engine.agents.trainer import load_model


def evaluate(
    parsed_json: dict,
    model_path: str,
    algorithm: str = "PPO",
    num_games: int = 1000,
    num_players: int = 2,
) -> dict:
    """
    학습된 모델로 N판 평가 게임 실행, 통계 수집.

    Returns:
        {
            "total_games": int,
            "win_rates": {player_id: float},
            "draw_rate": float,
            "avg_game_length": float,
            "game_length_std": float,
            "first_player_win_rate": float,
            "action_distribution": {action: count},
            "avg_net_worth": {player_id: float},
            "property_stats": {space_name: {"buy_rate": float, "avg_rent_collected": float}},
        }
    """
    model = load_model(model_path, algorithm)
    env = create_environment(parsed_json, num_players=num_players)

    wins = defaultdict(int)
    draws = 0
    game_lengths = []
    action_counts = defaultdict(int)
    player_net_worths = defaultdict(list)
    property_buys = defaultdict(int)
    total_games_played = 0

    for game_idx in range(num_games):
        obs, info = env.reset()
        done = False
        turn = 0

        while not done:
            current = env.current_player

            if current == 0:
                # 학습된 에이전트
                action, _ = model.predict(obs, deterministic=True)
                action = int(action)
            else:
                # 상대: 학습된 모델 사용 (self-play 평가)
                action, _ = model.predict(obs, deterministic=False)
                action = int(action)

            action_counts[action] += 1
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            turn += 1

        # 결과 집계
        game_lengths.append(turn)

        if env.winner is not None:
            wins[env.winner] += 1
        else:
            draws += 1

        # 순자산 기록
        for p_info in info.get("players", []):
            player_net_worths[p_info["id"]].append(p_info["net_worth"])

        # 부동산 매입 기록
        for space in env.config.spaces:
            if space.owner != -1:
                property_buys[space.name] += 1

        total_games_played += 1

    # 통계 계산
    win_rates = {
        str(pid): count / total_games_played
        for pid, count in wins.items()
    }

    # 모든 플레이어에 대해 빈 승률도 채우기
    for pid in range(num_players):
        if str(pid) not in win_rates:
            win_rates[str(pid)] = 0.0

    avg_net_worth = {
        str(pid): float(np.mean(worths)) if worths else 0.0
        for pid, worths in player_net_worths.items()
    }

    property_stats = {
        name: {"buy_rate": count / total_games_played}
        for name, count in property_buys.items()
    }

    return {
        "total_games": total_games_played,
        "win_rates": win_rates,
        "draw_rate": draws / total_games_played,
        "avg_game_length": float(np.mean(game_lengths)),
        "game_length_std": float(np.std(game_lengths)),
        "first_player_win_rate": win_rates.get("0", 0.0),
        "action_distribution": dict(action_counts),
        "avg_net_worth": avg_net_worth,
        "property_stats": property_stats,
    }
