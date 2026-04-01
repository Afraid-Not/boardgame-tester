"""지배 전략 탐지. 평가 데이터에서 과도하게 효과적인 전략/패턴 식별."""


def detect_dominant_strategies(
    eval_result: dict,
    parsed_json: dict,
) -> list[dict]:
    """
    평가 결과에서 지배 전략을 탐지.

    Returns:
        [
            {
                "name": str,
                "description": str,
                "evidence": str,
                "impact": "high" | "medium" | "low",
            }
        ]
    """
    strategies = []

    # 1. 액션 편중 분석
    action_dist = eval_result.get("action_distribution", {})
    total = sum(action_dist.values()) if action_dist else 1

    action_names = {
        0: "Pass/End turn",
        1: "Buy property",
        2: "Build house",
        3: "Mortgage",
        4: "Unmortgage",
    }

    for action_id, count in action_dist.items():
        ratio = count / total
        action_id = int(action_id)
        name = action_names.get(action_id, f"Action {action_id}")

        if action_id == 1 and ratio > 0.3:
            strategies.append({
                "name": "Aggressive buying",
                "description": "Agent buys properties at every opportunity",
                "evidence": f"Buy action used {ratio:.0%} of the time",
                "impact": "medium",
            })
        elif action_id == 0 and ratio > 0.7:
            strategies.append({
                "name": "Passive play dominance",
                "description": "Passing/doing nothing is the most common action, suggesting limited meaningful choices",
                "evidence": f"Pass action used {ratio:.0%} of the time",
                "impact": "high",
            })
        elif action_id == 3 and ratio > 0.15:
            strategies.append({
                "name": "Mortgage cycling",
                "description": "Heavy reliance on mortgaging properties for cash",
                "evidence": f"Mortgage action used {ratio:.0%} of the time",
                "impact": "medium",
            })

    # 2. 부동산 매입 편중 분석
    property_stats = eval_result.get("property_stats", {})
    if property_stats:
        buy_rates = [(name, s["buy_rate"]) for name, s in property_stats.items()]
        buy_rates.sort(key=lambda x: x[1], reverse=True)

        if len(buy_rates) >= 2:
            top_rate = buy_rates[0][1]
            bottom_rate = buy_rates[-1][1]

            if top_rate > 0.8 and bottom_rate < 0.3:
                strategies.append({
                    "name": "Property hotspot",
                    "description": f"'{buy_rates[0][0]}' is bought {top_rate:.0%} of games while '{buy_rates[-1][0]}' only {bottom_rate:.0%}",
                    "evidence": "Huge disparity in property purchase rates suggests uneven property values",
                    "impact": "medium",
                })

    # 3. 선공 이점 분석
    first_wr = eval_result.get("first_player_win_rate", 0.5)
    num_players = len(eval_result.get("win_rates", {}))
    ideal = 1.0 / max(num_players, 1)

    if first_wr > ideal + 0.15:
        strategies.append({
            "name": "First-mover advantage",
            "description": "Going first provides a significant strategic advantage",
            "evidence": f"First player wins {first_wr:.0%} vs ideal {ideal:.0%}",
            "impact": "high",
        })
    elif first_wr < ideal - 0.15:
        strategies.append({
            "name": "Second-mover advantage",
            "description": "Going second is actually advantageous",
            "evidence": f"First player only wins {first_wr:.0%} vs ideal {ideal:.0%}",
            "impact": "medium",
        })

    # 4. 게임 길이 이상
    avg_len = eval_result.get("avg_game_length", 0)
    draw_rate = eval_result.get("draw_rate", 0)

    if draw_rate > 0.2:
        strategies.append({
            "name": "Stalemate tendency",
            "description": "Games frequently end in draws/timeouts",
            "evidence": f"Draw rate: {draw_rate:.0%}",
            "impact": "high",
        })

    return strategies
