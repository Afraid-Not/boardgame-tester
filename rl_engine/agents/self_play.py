"""Self-play 래퍼. 2인 게임에서 에이전트가 자기 자신과 대전."""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3.common.callbacks import BaseCallback


class SelfPlayWrapper(gym.Wrapper):
    """
    Self-play 환경 래퍼.

    학습 에이전트는 항상 player 0으로 플레이.
    상대(player 1+)는 opponent_policy로 행동 결정.
    opponent_policy가 None이면 랜덤 상대.
    """

    def __init__(self, env, opponent_policy=None):
        super().__init__(env)
        self.opponent_policy = opponent_policy

    def set_opponent(self, policy):
        """상대 정책 업데이트 (학습 중 주기적으로 호출)."""
        self.opponent_policy = policy

    def step(self, action):
        # Player 0 (학습 에이전트) 액션 실행
        obs, reward, terminated, truncated, info = self.env.step(action)

        # 게임 끝났으면 그대로 반환
        if terminated or truncated:
            return obs, reward, terminated, truncated, info

        # 상대 턴들 자동 실행 (player 0 차례가 올 때까지)
        while self.env.unwrapped.current_player != 0 and not terminated and not truncated:
            if self.opponent_policy is not None:
                opp_action, _ = self.opponent_policy.predict(obs, deterministic=False)
            else:
                opp_action = self.env.action_space.sample()

            obs, opp_reward, terminated, truncated, info = self.env.step(opp_action)

        # Player 0 관점 승패 보상
        if terminated or truncated:
            winner = self.env.unwrapped.winner
            if winner == 0:
                reward += 1.0
            elif winner is not None:
                reward -= 1.0

        return obs, reward, terminated, truncated, info


class SelfPlayCallback(BaseCallback):
    """학습 중 주기적으로 상대 정책을 현재 학습 모델로 업데이트."""

    def __init__(self, update_interval: int = 10000, verbose: int = 0):
        super().__init__(verbose)
        self.update_interval = update_interval

    def _on_step(self) -> bool:
        if self.num_timesteps % self.update_interval == 0 and self.num_timesteps > 0:
            # 현재 모델을 상대 정책으로 복사
            env = self.training_env.envs[0]
            if hasattr(env, "set_opponent"):
                env.set_opponent(self.model)
                if self.verbose > 0:
                    print(f"[SelfPlay] Updated opponent at step {self.num_timesteps}")
        return True


class ProgressCallback(BaseCallback):
    """학습 진행률을 추적하여 외부에서 조회 가능하게 함."""

    def __init__(self, total_timesteps: int, progress_store: dict, verbose: int = 0):
        super().__init__(verbose)
        self.total_timesteps_target = total_timesteps
        self.progress_store = progress_store

    def _on_step(self) -> bool:
        progress = min(
            int(self.num_timesteps / self.total_timesteps_target * 100), 99
        )
        self.progress_store["progress"] = progress
        self.progress_store["timesteps"] = self.num_timesteps

        # 중지 요청 확인
        if self.progress_store.get("stop_requested"):
            return False

        return True

    def _on_training_end(self) -> None:
        self.progress_store["progress"] = 100
