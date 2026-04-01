"""RL 환경 공통 인터페이스. 모든 게임 환경이 상속."""

from abc import abstractmethod
import gymnasium as gym
import numpy as np


class BaseBoardGameEnv(gym.Env):
    """보드게임 RL 환경 기본 클래스."""

    metadata = {"render_modes": ["human", "ansi"]}

    def __init__(self, num_players: int = 2, render_mode: str | None = None):
        super().__init__()
        self.num_players = num_players
        self.render_mode = render_mode
        self.current_player = 0
        self.done = False
        self.winner = None
        self.turn_count = 0
        self.max_turns = 1000  # 무한 게임 방지

    @abstractmethod
    def _get_obs(self) -> np.ndarray:
        """현재 관찰 상태 반환."""
        ...

    @abstractmethod
    def _get_info(self) -> dict:
        """추가 정보 반환."""
        ...

    @abstractmethod
    def _apply_action(self, action: int) -> float:
        """액션 적용 후 보상 반환."""
        ...

    def step(self, action: int):
        if self.done:
            return self._get_obs(), 0.0, True, False, self._get_info()

        reward = self._apply_action(action)

        self.turn_count += 1
        truncated = self.turn_count >= self.max_turns

        if truncated and not self.done:
            self.done = True
            # 턴 제한 도달 시 가장 부유한 플레이어 승리
            self._resolve_by_wealth()

        return self._get_obs(), reward, self.done, truncated, self._get_info()

    def _resolve_by_wealth(self):
        """턴 제한 시 자산 기준 승자 결정. 하위 클래스에서 오버라이드 가능."""
        pass

    def _next_player(self):
        """다음 플레이어로 턴 넘기기."""
        self.current_player = (self.current_player + 1) % self.num_players

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_player = 0
        self.done = False
        self.winner = None
        self.turn_count = 0
        return self._get_obs(), self._get_info()
