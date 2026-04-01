"""경제 보드게임 RL 환경 템플릿. 파싱된 게임 JSON을 받아 Gymnasium 환경 생성."""

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from rl_engine.environments.base_env import BaseBoardGameEnv
from rl_engine.environments.economic_board.components import (
    GameConfig,
    Player,
    SpaceType,
)


class EconomicBoardEnv(BaseBoardGameEnv):
    """
    경제 보드게임 Gymnasium 환경.

    Action Space (Discrete):
        0: 아무것도 안 함 / 턴 종료
        1: 현재 칸 구매
        2: 집 짓기 (가장 저렴한 소유 부동산에)
        3: 모기지 (가장 비싼 소유 부동산)
        4: 모기지 해제

    Observation Space:
        플레이어별: [position, money, num_properties, in_jail, net_worth]
        + 각 칸별: [owner, houses, price, current_rent]
    """

    # 액션 상수
    ACTION_PASS = 0
    ACTION_BUY = 1
    ACTION_BUILD = 2
    ACTION_MORTGAGE = 3
    ACTION_UNMORTGAGE = 4
    NUM_ACTIONS = 5

    def __init__(
        self,
        game_config: GameConfig,
        num_players: int = 2,
        render_mode: str | None = None,
    ):
        super().__init__(num_players=num_players, render_mode=render_mode)
        self.config = game_config
        self.players: list[Player] = []

        # Observation: 플레이어 정보 + 보드 상태
        player_obs_size = num_players * 5  # pos, money, props, jail, net_worth
        board_obs_size = game_config.total_spaces * 4  # owner, houses, price, rent
        obs_size = player_obs_size + board_obs_size + 1  # +1 for current_player

        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(self.NUM_ACTIONS)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # 플레이어 초기화
        self.players = [
            Player(id=i, money=self.config.starting_money)
            for i in range(self.num_players)
        ]

        # 보드 초기화 (소유권/집 리셋)
        for space in self.config.spaces:
            space.owner = -1
            space.houses = 0
            space.mortgaged = False

        return self._get_obs(), self._get_info()

    def _get_obs(self) -> np.ndarray:
        obs = []

        # 플레이어 정보
        for p in self.players:
            obs.extend([
                p.position / max(self.config.total_spaces, 1),
                p.money / max(self.config.starting_money, 1),
                len(p.properties) / max(self.config.total_spaces, 1),
                float(p.in_jail),
                self._calc_net_worth(p) / max(self.config.starting_money, 1),
            ])

        # 보드 상태
        for space in self.config.spaces:
            obs.extend([
                (space.owner + 1) / (self.num_players + 1),
                space.houses / max(self.config.house_max + 1, 1),
                space.price / max(self.config.starting_money, 1),
                space.current_rent / max(self.config.starting_money, 1),
            ])

        # 현재 플레이어
        obs.append(self.current_player / max(self.num_players, 1))

        return np.array(obs, dtype=np.float32)

    def _get_info(self) -> dict:
        return {
            "current_player": self.current_player,
            "turn": self.turn_count,
            "players": [
                {
                    "id": p.id,
                    "money": p.money,
                    "position": p.position,
                    "properties": len(p.properties),
                    "bankrupt": p.bankrupt,
                    "net_worth": self._calc_net_worth(p),
                }
                for p in self.players
            ],
        }

    def _apply_action(self, action: int) -> float:
        player = self.players[self.current_player]
        if player.bankrupt:
            self._next_player()
            return 0.0

        reward = 0.0

        # 감옥 처리
        if player.in_jail:
            player.jail_turns += 1
            if player.jail_turns >= 3:
                player.in_jail = False
                player.jail_turns = 0
                player.money -= 50  # 보석금
            else:
                self._next_player()
                return 0.0

        # 주사위 굴리기
        dice_total = self._roll_dice()
        old_pos = player.position
        player.position = (player.position + dice_total) % self.config.total_spaces

        # 출발점 통과 보너스
        if self.config.layout == "loop" and player.position < old_pos:
            player.money += self.config.pass_go_bonus
            reward += 0.1

        # 현재 칸 처리
        space = self._get_space(player.position)
        reward += self._handle_landing(player, space, action)

        # 파산 체크
        if player.money < 0:
            self._handle_bankruptcy(player)

        # 게임 종료 체크
        active = [p for p in self.players if not p.bankrupt]
        if len(active) <= 1:
            self.done = True
            if active:
                self.winner = active[0].id

        self._next_player()
        # 다음 플레이어가 파산이면 건너뛰기
        while not self.done and self.players[self.current_player].bankrupt:
            self._next_player()

        return reward

    def _roll_dice(self) -> int:
        total = 0
        for _ in range(self.config.dice_count):
            total += self.np_random.integers(1, self.config.dice_sides + 1)
        return total

    def _get_space(self, position: int):
        for s in self.config.spaces:
            if s.index == position:
                return s
        return self.config.spaces[0]

    def _handle_landing(self, player: Player, space, action: int) -> float:
        reward = 0.0

        if space.type == SpaceType.GO_TO_JAIL:
            player.in_jail = True
            player.jail_turns = 0
            # jail 칸으로 이동
            jail_spaces = [s for s in self.config.spaces if s.type == SpaceType.JAIL]
            if jail_spaces:
                player.position = jail_spaces[0].index
            return -0.1

        if space.type == SpaceType.TAX:
            tax_amount = space.price if space.price > 0 else 200
            player.money -= tax_amount
            return -0.05

        # 구매 가능한 칸
        if space.is_buyable and space.owner == -1 and action == self.ACTION_BUY:
            if player.money >= space.price:
                player.money -= space.price
                space.owner = player.id
                player.properties.append(space.index)
                reward += 0.2

        # 임대료 지불
        elif space.is_buyable and space.owner != -1 and space.owner != player.id:
            rent = space.current_rent
            # 완전 세트 보너스
            if space.group and space.houses == 0:
                group_props = self.config.get_group_properties(space.group)
                if all(s.owner == space.owner for s in group_props):
                    rent *= 2
            player.money -= rent
            self.players[space.owner].money += rent
            reward -= 0.1

        # 집 짓기
        if action == self.ACTION_BUILD:
            reward += self._try_build(player)

        # 모기지
        if action == self.ACTION_MORTGAGE:
            reward += self._try_mortgage(player)

        # 모기지 해제
        if action == self.ACTION_UNMORTGAGE:
            reward += self._try_unmortgage(player)

        return reward

    def _try_build(self, player: Player) -> float:
        """소유 부동산 중 가장 저렴한 곳에 집 짓기."""
        buildable = []
        for idx in player.properties:
            space = self._get_space(idx)
            if (
                space.type == SpaceType.PROPERTY
                and space.houses < self.config.house_max
                and not space.mortgaged
                and space.house_cost > 0
                and player.money >= space.house_cost
            ):
                # 완전 세트 필요 여부 체크
                if self.config.requires_complete_set:
                    group_props = self.config.get_group_properties(space.group)
                    if not all(s.owner == player.id for s in group_props):
                        continue
                buildable.append(space)

        if not buildable:
            return 0.0

        # 가장 저렴한 곳에 건설
        target = min(buildable, key=lambda s: s.house_cost)
        player.money -= target.house_cost
        target.houses += 1
        return 0.15

    def _try_mortgage(self, player: Player) -> float:
        """가장 비싼 소유 부동산 모기지."""
        mortgageable = []
        for idx in player.properties:
            space = self._get_space(idx)
            if not space.mortgaged and space.houses == 0:
                mortgageable.append(space)

        if not mortgageable:
            return 0.0

        target = max(mortgageable, key=lambda s: s.mortgage_value)
        target.mortgaged = True
        player.money += target.mortgage_value
        return -0.05

    def _try_unmortgage(self, player: Player) -> float:
        """모기지 해제."""
        mortgaged = []
        for idx in player.properties:
            space = self._get_space(idx)
            if space.mortgaged:
                mortgaged.append(space)

        if not mortgaged:
            return 0.0

        target = min(mortgaged, key=lambda s: s.mortgage_value)
        cost = int(target.mortgage_value * 1.1)  # 10% 이자
        if player.money >= cost:
            player.money -= cost
            target.mortgaged = False
            return 0.05
        return 0.0

    def _handle_bankruptcy(self, player: Player):
        """플레이어 파산 처리."""
        player.bankrupt = True
        # 소유 부동산 해제
        for idx in player.properties:
            space = self._get_space(idx)
            space.owner = -1
            space.houses = 0
            space.mortgaged = False
        player.properties.clear()

    def _calc_net_worth(self, player: Player) -> int:
        """총 자산 계산 (현금 + 부동산 가치 + 건물 가치)."""
        total = player.money
        for idx in player.properties:
            space = self._get_space(idx)
            total += space.price
            total += space.houses * space.house_cost
        return total

    def _resolve_by_wealth(self):
        """턴 제한 시 자산 기준 승자 결정."""
        active = [p for p in self.players if not p.bankrupt]
        if active:
            best = max(active, key=lambda p: self._calc_net_worth(p))
            self.winner = best.id

    def render(self):
        if self.render_mode == "ansi":
            lines = [f"=== Turn {self.turn_count} ==="]
            for p in self.players:
                status = "BANKRUPT" if p.bankrupt else f"pos={p.position}, ${p.money}"
                lines.append(f"Player {p.id}: {status}")
            return "\n".join(lines)
