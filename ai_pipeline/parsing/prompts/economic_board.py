"""경제 보드게임 규칙 파싱용 프롬프트 템플릿."""

import json
import os

# JSON 스키마 로드 (검증용)
_schema_path = os.path.join(os.path.dirname(__file__), "..", "schemas", "economic_board.json")
with open(_schema_path, "r", encoding="utf-8") as f:
    ECONOMIC_BOARD_SCHEMA = json.load(f)

SYSTEM_PROMPT = """You are a board game rules parser. Your job is to extract structured game information from board game rulebooks and convert it into a precise JSON format suitable for reinforcement learning environment generation.

You must be thorough and accurate. Extract every detail about:
- Board layout (all spaces, their types, costs, rents)
- Player setup (starting money, pieces, cards)
- Turn structure (phases, actions available)
- Win/loss conditions
- Special rules and exceptions

If information is ambiguous or missing, make reasonable inferences based on similar well-known economic board games, but mark inferred values with a comment in the special_rules section.

IMPORTANT: Return a flat JSON data object with actual values, NOT a JSON Schema definition."""

RAG_CONTEXT_TEMPLATE = """Here are similar existing board games for reference. Use these to fill in gaps or validate your parsing:

{references}

---

"""

EXAMPLE_OUTPUT = """{
  "type": "economic_board",
  "name": "Example Game",
  "players": { "min": 2, "max": 4 },
  "turn_based": true,
  "components": {
    "board": {
      "total_spaces": 10,
      "layout": "loop",
      "spaces": [
        { "index": 0, "type": "start", "name": "Go" },
        { "index": 1, "type": "property", "name": "Park A", "group": "blue", "price": 100, "rent": [10, 30, 90], "house_cost": 50 },
        { "index": 2, "type": "tax", "name": "Tax", "price": 200 },
        { "index": 3, "type": "chance", "name": "Chance" },
        { "index": 4, "type": "jail", "name": "Jail" },
        { "index": 5, "type": "go_to_jail", "name": "Go to Jail" },
        { "index": 6, "type": "free_parking", "name": "Free Parking" },
        { "index": 7, "type": "event", "name": "Event" },
        { "index": 8, "type": "railroad", "name": "Railroad", "price": 200, "rent": [25, 50] },
        { "index": 9, "type": "property", "name": "Park B", "group": "blue", "price": 120, "rent": [12, 36, 100], "house_cost": 50 }
      ]
    },
    "dice": { "count": 2, "sides": 6 },
    "starting_money": 1500,
    "pass_go_bonus": 200,
    "currency_unit": "$",
    "buildings": { "house_max": 4, "hotel_max": 1, "requires_complete_set": true }
  },
  "phases": ["roll_dice", "move", "action", "end_turn"],
  "win_condition": "last_player_standing",
  "special_rules": [
    { "name": "Doubles", "description": "Rolling doubles gives extra turn", "trigger": "dice_roll", "effect": "extra_turn" }
  ]
}"""

PARSE_PROMPT_TEMPLATE = """{rag_context}Now parse the following board game rulebook into a structured JSON object.

## Rulebook Text:
{rules_text}

## Example Output Format:
Here is an example of the expected JSON structure (your output should follow this exact format with actual game data):

{example}

## Space types you can use:
start, property, railroad, utility, tax, chance, community_chest, jail, go_to_jail, free_parking, event, special, empty

## Win condition options:
last_player_standing, most_money, first_to_target, most_points

## Important:
1. List EVERY board space with index, type, name, and relevant properties
2. Group properties by their color/category set
3. Rent array: [base_rent, with_1_building, with_2_buildings, ...]
4. Include all special rules
5. Return ONLY a JSON data object (NOT a JSON Schema), no markdown, no explanation"""

IMAGE_PARSE_PROMPT = """Analyze this board game rulebook image and extract the game rules in detail.

Describe:
1. The board layout (number of spaces, types of spaces, arrangement)
2. Each space on the board (name, type, cost, rent if visible)
3. Player setup rules (starting money, pieces)
4. Turn structure and phases
5. Win/loss conditions
6. Any special rules, cards, or mechanics visible

Be as detailed and specific as possible. Include exact numbers, costs, and values wherever visible."""
