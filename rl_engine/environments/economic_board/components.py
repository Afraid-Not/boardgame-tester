"""경제 보드게임 컴포넌트 정의."""

from dataclasses import dataclass, field
from enum import Enum


class SpaceType(str, Enum):
    START = "start"
    PROPERTY = "property"
    RAILROAD = "railroad"
    UTILITY = "utility"
    TAX = "tax"
    CHANCE = "chance"
    COMMUNITY_CHEST = "community_chest"
    JAIL = "jail"
    GO_TO_JAIL = "go_to_jail"
    FREE_PARKING = "free_parking"
    EVENT = "event"
    SPECIAL = "special"
    EMPTY = "empty"


@dataclass
class Space:
    index: int
    type: SpaceType
    name: str
    group: str = ""
    price: int = 0
    rent: list[int] = field(default_factory=list)
    house_cost: int = 0
    mortgage_value: int = 0
    owner: int = -1  # -1 = no owner
    houses: int = 0
    mortgaged: bool = False

    @property
    def is_buyable(self) -> bool:
        return self.type in (SpaceType.PROPERTY, SpaceType.RAILROAD, SpaceType.UTILITY)

    @property
    def current_rent(self) -> int:
        if self.mortgaged or self.owner == -1:
            return 0
        if not self.rent:
            return 0
        idx = min(self.houses, len(self.rent) - 1)
        return self.rent[idx]


@dataclass
class Player:
    id: int
    money: int
    position: int = 0
    properties: list[int] = field(default_factory=list)  # space indices
    in_jail: bool = False
    jail_turns: int = 0
    bankrupt: bool = False
    doubles_count: int = 0

    @property
    def net_worth(self) -> int:
        return self.money  # properties value added by env


@dataclass
class GameConfig:
    """파싱된 JSON에서 생성되는 게임 설정."""
    name: str
    num_players_min: int
    num_players_max: int
    total_spaces: int
    spaces: list[Space]
    dice_count: int = 2
    dice_sides: int = 6
    starting_money: int = 1500
    pass_go_bonus: int = 200
    house_max: int = 4
    hotel_max: int = 1
    requires_complete_set: bool = True
    currency_unit: str = "$"
    layout: str = "loop"
    special_rules: list[dict] = field(default_factory=list)

    @classmethod
    def from_parsed_json(cls, data: dict) -> "GameConfig":
        """파싱된 게임 JSON에서 GameConfig 생성."""
        components = data.get("components", {})
        board = components.get("board", {})
        dice = components.get("dice", {"count": 2, "sides": 6})
        buildings = components.get("buildings", {})

        spaces = []
        for s in board.get("spaces", []):
            spaces.append(Space(
                index=s["index"],
                type=SpaceType(s["type"]),
                name=s["name"],
                group=s.get("group", ""),
                price=int(s.get("price", 0)),
                rent=[int(r) for r in s.get("rent", [])],
                house_cost=int(s.get("house_cost", 0)),
                mortgage_value=int(s.get("mortgage_value", 0)),
            ))

        return cls(
            name=data.get("name", "Unknown"),
            num_players_min=data.get("players", {}).get("min", 2),
            num_players_max=data.get("players", {}).get("max", 4),
            total_spaces=board.get("total_spaces", len(spaces)),
            spaces=spaces,
            dice_count=dice.get("count", 2),
            dice_sides=dice.get("sides", 6),
            starting_money=int(components.get("starting_money", 1500)),
            pass_go_bonus=int(components.get("pass_go_bonus", 200)),
            house_max=buildings.get("house_max", 4),
            hotel_max=buildings.get("hotel_max", 1),
            requires_complete_set=buildings.get("requires_complete_set", True),
            currency_unit=components.get("currency_unit", "$"),
            layout=board.get("layout", "loop"),
            special_rules=data.get("special_rules", []),
        )

    def get_group_properties(self, group: str) -> list[Space]:
        """같은 그룹의 모든 부동산 반환."""
        return [s for s in self.spaces if s.group == group and s.is_buyable]
