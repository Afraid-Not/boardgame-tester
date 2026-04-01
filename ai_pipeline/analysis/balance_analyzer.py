"""밸런스 점수 산출 및 종합 분석."""

import numpy as np


def analyze_balance(eval_result: dict, parsed_json: dict) -> dict:
    """
    평가 결과에서 밸런스 지표를 산출.

    Args:
        eval_result: evaluator.evaluate()의 반환값
        parsed_json: 파싱된 게임 JSON

    Returns:
        {
            "balance_score": float (0-100, 50=perfect),
            "severity": "good" | "warning" | "critical",
            "metrics": {
                "win_rate_variance": float,
                "first_player_advantage": float,
                "game_length_score": float,
                "strategy_diversity": float,
            },
            "issues": [{"type": str, "description": str, "severity": str}],
        }
    """
    win_rates = eval_result.get("win_rates", {})
    rates = list(win_rates.values())
    num_players = len(rates)

    issues = []

    # 1. 승률 균형 (50점 만점)
    if num_players >= 2:
        ideal_rate = 1.0 / num_players
        variance = np.var(rates)
        max_deviation = max(abs(r - ideal_rate) for r in rates)
        win_rate_score = max(0, 50 - max_deviation * 200)

        if max_deviation > 0.15:
            dominant = max(win_rates, key=win_rates.get)
            issues.append({
                "type": "win_rate_imbalance",
                "description": f"Player {dominant} has {win_rates[dominant]:.0%} win rate (ideal: {ideal_rate:.0%})",
                "severity": "critical" if max_deviation > 0.25 else "warning",
            })
    else:
        win_rate_score = 50
        variance = 0
        max_deviation = 0

    # 2. 선공 이점 (15점 만점)
    first_wr = eval_result.get("first_player_win_rate", 0.5)
    first_adv = abs(first_wr - (1.0 / max(num_players, 1)))
    first_player_score = max(0, 15 - first_adv * 100)

    if first_adv > 0.1:
        issues.append({
            "type": "first_player_advantage",
            "description": f"First player win rate {first_wr:.0%} deviates from ideal {1/num_players:.0%}",
            "severity": "warning" if first_adv < 0.2 else "critical",
        })

    # 3. 게임 길이 적정성 (15점 만점)
    avg_length = eval_result.get("avg_game_length", 0)
    length_std = eval_result.get("game_length_std", 0)

    # 너무 짧거나 너무 긴 게임은 감점
    if avg_length < 20:
        game_length_score = avg_length / 20 * 15
        issues.append({
            "type": "game_too_short",
            "description": f"Average game length is {avg_length:.0f} turns (too short for meaningful strategy)",
            "severity": "warning",
        })
    elif avg_length > 500:
        game_length_score = max(0, 15 - (avg_length - 500) / 100)
        issues.append({
            "type": "game_too_long",
            "description": f"Average game length is {avg_length:.0f} turns (games drag on too long)",
            "severity": "warning",
        })
    else:
        game_length_score = 15

    # 게임 길이 분산이 너무 큰 경우
    if length_std > avg_length * 0.8 and avg_length > 0:
        issues.append({
            "type": "game_length_inconsistent",
            "description": f"Game length varies widely (avg {avg_length:.0f} +/- {length_std:.0f} turns)",
            "severity": "warning",
        })

    # 4. 전략 다양성 (20점 만점)
    action_dist = eval_result.get("action_distribution", {})
    total_actions = sum(action_dist.values()) if action_dist else 1
    action_probs = [v / total_actions for v in action_dist.values()] if action_dist else []

    if action_probs:
        # 엔트로피 기반 다양성
        entropy = -sum(p * np.log(p + 1e-10) for p in action_probs)
        max_entropy = np.log(len(action_probs) + 1e-10)
        diversity_ratio = entropy / max_entropy if max_entropy > 0 else 0
        strategy_score = diversity_ratio * 20

        if diversity_ratio < 0.3:
            dominant_action = max(action_dist, key=action_dist.get)
            issues.append({
                "type": "low_strategy_diversity",
                "description": f"Action {dominant_action} dominates ({action_dist[dominant_action]/total_actions:.0%} of all actions)",
                "severity": "warning",
            })
    else:
        strategy_score = 10
        diversity_ratio = 0.5

    # 종합 점수
    balance_score = win_rate_score + first_player_score + game_length_score + strategy_score
    balance_score = round(max(0, min(100, balance_score)), 2)

    # 심각도
    if balance_score >= 60:
        severity = "good"
    elif balance_score >= 40:
        severity = "warning"
    else:
        severity = "critical"

    return {
        "balance_score": balance_score,
        "severity": severity,
        "metrics": {
            "win_rate_variance": round(float(variance), 4),
            "first_player_advantage": round(float(first_adv), 4),
            "game_length_score": round(game_length_score, 2),
            "strategy_diversity": round(float(diversity_ratio), 4) if action_probs else 0.5,
        },
        "issues": issues,
    }
