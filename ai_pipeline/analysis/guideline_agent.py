"""OpenAI API 기반 밸런스 개선 가이드라인 생성."""

import json
from openai import OpenAI


GUIDELINE_SYSTEM_PROMPT = """You are a board game balance expert. Given a game's rules and balance analysis data, you generate specific, actionable improvement guidelines.

Your guidelines must:
1. Reference specific game elements (property names, costs, rent values, etc.)
2. Include concrete numerical adjustments (e.g., "Reduce rent from 300 to 200")
3. Explain WHY each change improves balance
4. Estimate the expected impact on the identified issues
5. Be ordered by priority (most impactful first)

Format each guideline as a JSON object."""

GUIDELINE_PROMPT_TEMPLATE = """Analyze this board game's balance issues and generate specific improvement guidelines.

## Game Rules (JSON):
{game_json}

## Balance Analysis:
- Balance Score: {balance_score}/100 (50 = perfect balance)
- Severity: {severity}
- Win Rates: {win_rates}
- First Player Win Rate: {first_player_wr}
- Average Game Length: {avg_game_length} turns
- Draw Rate: {draw_rate}

## Identified Issues:
{issues}

## Dominant Strategies Detected:
{dominant_strategies}

## Property Statistics:
{property_stats}

## Action Distribution:
{action_distribution}

---

Generate 3-7 specific improvement guidelines. Return a JSON array where each element has:
- "priority": 1-5 (1 = highest)
- "category": "pricing" | "rules" | "board_layout" | "mechanics" | "balance"
- "title": short title
- "description": detailed explanation
- "changes": [{{"target": "what to change", "from": "current value", "to": "suggested value"}}]
- "expected_impact": what this change should fix

Return ONLY the JSON array, no other text."""


def generate_guidelines(
    parsed_json: dict,
    balance_result: dict,
    eval_result: dict,
    dominant_strategies: list[dict],
    api_key: str,
    model: str = "gpt-4o",
) -> list[dict]:
    """
    밸런스 분석 결과를 기반으로 구체적 개선 가이드라인 생성.

    Returns:
        가이드라인 목록 [{priority, category, title, description, changes, expected_impact}]
    """
    client = OpenAI(api_key=api_key)

    # 이슈 포맷팅
    issues_text = "\n".join(
        f"- [{i['severity'].upper()}] {i['type']}: {i['description']}"
        for i in balance_result.get("issues", [])
    ) or "No specific issues detected."

    strategies_text = "\n".join(
        f"- [{s['impact'].upper()}] {s['name']}: {s['description']} (Evidence: {s['evidence']})"
        for s in dominant_strategies
    ) or "No dominant strategies detected."

    prompt = GUIDELINE_PROMPT_TEMPLATE.format(
        game_json=json.dumps(parsed_json, ensure_ascii=False, indent=2)[:4000],
        balance_score=balance_result.get("balance_score", 50),
        severity=balance_result.get("severity", "unknown"),
        win_rates=json.dumps(eval_result.get("win_rates", {})),
        first_player_wr=f"{eval_result.get('first_player_win_rate', 0.5):.0%}",
        avg_game_length=f"{eval_result.get('avg_game_length', 0):.0f}",
        draw_rate=f"{eval_result.get('draw_rate', 0):.0%}",
        issues=issues_text,
        dominant_strategies=strategies_text,
        property_stats=json.dumps(eval_result.get("property_stats", {}), indent=2)[:1000],
        action_distribution=json.dumps(eval_result.get("action_distribution", {})),
    )

    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": GUIDELINE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    raw = response.choices[0].message.content.strip()
    return _extract_json_array(raw)


def _extract_json_array(text: str) -> list[dict]:
    """JSON 배열 추출."""
    if "```" in text:
        start = text.find("```")
        content_start = text.find("\n", start) + 1
        end = text.find("```", content_start)
        if end != -1:
            text = text[content_start:end].strip()

    return json.loads(text)
