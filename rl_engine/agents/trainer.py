"""SB3 기반 학습 실행기."""

import os
import json
from pathlib import Path

from stable_baselines3 import PPO, DQN, A2C
from stable_baselines3.common.env_util import make_vec_env

from rl_engine.codegen.generator import create_environment
from rl_engine.agents.self_play import SelfPlayWrapper, SelfPlayCallback, ProgressCallback


ALGO_MAP = {
    "PPO": PPO,
    "DQN": DQN,
    "A2C": A2C,
}

DEFAULT_HYPERPARAMS = {
    "PPO": {
        "learning_rate": 3e-4,
        "n_steps": 2048,
        "batch_size": 64,
        "n_epochs": 10,
        "gamma": 0.99,
        "ent_coef": 0.01,
    },
    "DQN": {
        "learning_rate": 1e-4,
        "buffer_size": 50000,
        "batch_size": 64,
        "gamma": 0.99,
        "exploration_fraction": 0.2,
    },
    "A2C": {
        "learning_rate": 7e-4,
        "n_steps": 5,
        "gamma": 0.99,
        "ent_coef": 0.01,
    },
}


def train(
    parsed_json: dict,
    algorithm: str = "PPO",
    hyperparameters: dict | None = None,
    total_timesteps: int = 100000,
    num_players: int = 2,
    checkpoint_dir: str = "rl_engine/checkpoints",
    job_id: str = "default",
    progress_store: dict | None = None,
) -> dict:
    """
    게임 환경에서 RL 에이전트를 학습.

    Args:
        parsed_json: 파싱된 게임 JSON
        algorithm: PPO / DQN / A2C
        hyperparameters: 하이퍼파라미터 오버라이드
        total_timesteps: 총 학습 스텝
        num_players: 플레이어 수
        checkpoint_dir: 모델 저장 디렉토리
        job_id: 학습 작업 ID
        progress_store: 진행률 공유 dict

    Returns:
        학습 결과 dict
    """
    if progress_store is None:
        progress_store = {"progress": 0, "timesteps": 0}

    # 알고리즘 선택
    algo_cls = ALGO_MAP.get(algorithm)
    if algo_cls is None:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Use one of {list(ALGO_MAP.keys())}")

    # 하이퍼파라미터 병합
    params = DEFAULT_HYPERPARAMS.get(algorithm, {}).copy()
    if hyperparameters:
        params.update(hyperparameters)

    # 환경 생성 + self-play 래퍼
    base_env = create_environment(parsed_json, num_players=num_players)
    env = SelfPlayWrapper(base_env)

    # 모델 생성
    # DQN은 policy가 "MlpPolicy"
    model = algo_cls(
        "MlpPolicy",
        env,
        verbose=0,
        device="auto",
        **params,
    )

    # 콜백 설정
    callbacks = [
        ProgressCallback(total_timesteps, progress_store),
    ]

    # Self-play는 PPO/A2C에서만 (on-policy)
    if algorithm in ("PPO", "A2C"):
        callbacks.append(SelfPlayCallback(update_interval=total_timesteps // 10))

    # 학습 실행
    model.learn(
        total_timesteps=total_timesteps,
        callback=callbacks,
    )

    # 모델 저장
    save_dir = Path(checkpoint_dir) / job_id
    save_dir.mkdir(parents=True, exist_ok=True)
    model_path = save_dir / "model"
    model.save(str(model_path))

    # 학습 설정 저장
    config_path = save_dir / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({
            "algorithm": algorithm,
            "hyperparameters": params,
            "total_timesteps": total_timesteps,
            "num_players": num_players,
            "game_name": parsed_json.get("name", "Unknown"),
        }, f, indent=2, ensure_ascii=False)

    return {
        "model_path": str(model_path),
        "total_timesteps": total_timesteps,
        "algorithm": algorithm,
    }


def load_model(model_path: str, algorithm: str = "PPO"):
    """저장된 모델 로드."""
    algo_cls = ALGO_MAP.get(algorithm)
    if algo_cls is None:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    return algo_cls.load(model_path)
