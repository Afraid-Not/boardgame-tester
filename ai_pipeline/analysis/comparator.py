"""Before/After 밸런스 비교."""

import copy
import json


def apply_guidelines(parsed_json: dict, guidelines: list[dict]) -> dict:
    """
    가이드라인의 changes를 게임 JSON에 적용하여 수정된 버전 반환.

    각 change의 target 형식:
    - "spaces[index].field" (예: "spaces[1].price", "spaces[3].rent[0]")
    - "components.field" (예: "components.starting_money")
    - "components.dice.count"
    """
    modified = copy.deepcopy(parsed_json)
    applied = []

    for guideline in guidelines:
        for change in guideline.get("changes", []):
            target = change.get("target", "")
            new_value = change.get("to")

            if new_value is None:
                continue

            try:
                if _apply_change(modified, target, new_value):
                    applied.append({
                        "target": target,
                        "from": change.get("from"),
                        "to": new_value,
                        "guideline": guideline.get("title", ""),
                    })
            except (KeyError, IndexError, TypeError):
                continue

    return modified


def _apply_change(data: dict, target: str, value) -> bool:
    """target 경로를 파싱하여 값을 적용."""
    components = data.get("components", {})
    board = components.get("board", {})
    spaces = board.get("spaces", [])

    # spaces[N].field 패턴
    if target.startswith("spaces["):
        bracket_end = target.index("]")
        idx = int(target[7:bracket_end])
        rest = target[bracket_end + 2:]  # ".field" → "field"

        space = None
        for s in spaces:
            if s.get("index") == idx:
                space = s
                break

        if space is None:
            return False

        # rent[N] 같은 중첩 배열
        if "[" in rest:
            field = rest[:rest.index("[")]
            arr_idx = int(rest[rest.index("[") + 1:rest.index("]")])
            if field in space and isinstance(space[field], list) and arr_idx < len(space[field]):
                space[field][arr_idx] = _cast_value(value, space[field][arr_idx])
                return True
        else:
            if rest in space:
                space[rest] = _cast_value(value, space[rest])
                return True

    # components.field 패턴
    elif target.startswith("components."):
        path = target[11:].split(".")
        obj = components
        for key in path[:-1]:
            if key in obj:
                obj = obj[key]
            else:
                return False
        final_key = path[-1]
        if final_key in obj:
            obj[final_key] = _cast_value(value, obj[final_key])
            return True

    return False


def _cast_value(new_val, old_val):
    """기존 값의 타입에 맞게 캐스팅."""
    if isinstance(old_val, int):
        return int(new_val) if not isinstance(new_val, int) else new_val
    if isinstance(old_val, float):
        return float(new_val)
    return new_val


def compare_reports(before: dict, after: dict) -> dict:
    """
    두 밸런스 리포트를 비교.

    Returns:
        {
            "score_change": float,
            "severity_change": str,
            "improved_metrics": [...],
            "worsened_metrics": [...],
            "unchanged_metrics": [...],
        }
    """
    score_before = before.get("balance_score", 50)
    score_after = after.get("balance_score", 50)

    improved = []
    worsened = []
    unchanged = []

    before_metrics = before.get("metrics", {})
    after_metrics = after.get("metrics", {})

    for key in set(list(before_metrics.keys()) + list(after_metrics.keys())):
        b = before_metrics.get(key, 0)
        a = after_metrics.get(key, 0)
        diff = a - b

        entry = {"metric": key, "before": b, "after": a, "change": round(diff, 4)}

        # 대부분의 지표는 낮을수록 좋음 (variance, advantage 등)
        # game_length_score와 strategy_diversity는 높을수록 좋음
        better_higher = key in ("game_length_score", "strategy_diversity")

        if abs(diff) < 0.001:
            unchanged.append(entry)
        elif (diff > 0 and better_higher) or (diff < 0 and not better_higher):
            improved.append(entry)
        else:
            worsened.append(entry)

    return {
        "score_change": round(score_after - score_before, 2),
        "score_before": score_before,
        "score_after": score_after,
        "severity_before": before.get("severity", "unknown"),
        "severity_after": after.get("severity", "unknown"),
        "improved_metrics": improved,
        "worsened_metrics": worsened,
        "unchanged_metrics": unchanged,
    }
