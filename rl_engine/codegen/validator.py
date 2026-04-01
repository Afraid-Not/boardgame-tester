"""생성된 RL 환경 코드 검증."""

import traceback
import numpy as np
from rl_engine.codegen.generator import create_environment


def validate_environment(parsed_json: dict, num_steps: int = 100) -> dict:
    """
    생성된 환경이 정상 동작하는지 검증.

    Args:
        parsed_json: 파싱된 게임 JSON
        num_steps: 테스트할 스텝 수

    Returns:
        검증 결과 dict:
        {
            "valid": bool,
            "errors": list[str],
            "warnings": list[str],
            "stats": {"obs_shape": tuple, "num_actions": int, ...}
        }
    """
    result = {"valid": True, "errors": [], "warnings": [], "stats": {}}

    # 1. 환경 생성 테스트
    try:
        env = create_environment(parsed_json, num_players=2)
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Environment creation failed: {e}")
        return result

    # 2. reset 테스트
    try:
        obs, info = env.reset(seed=42)
        result["stats"]["obs_shape"] = obs.shape
        result["stats"]["num_actions"] = env.action_space.n
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Reset failed: {e}")
        return result

    # 3. observation space 체크
    if not env.observation_space.contains(obs):
        result["errors"].append("Initial observation out of observation_space bounds")
        result["valid"] = False

    # 4. 스텝 실행 테스트
    games_completed = 0
    errors_in_step = 0

    for i in range(num_steps):
        try:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)

            if not isinstance(reward, (int, float)):
                result["warnings"].append(f"Step {i}: reward is not numeric: {type(reward)}")

            if not env.observation_space.contains(obs):
                result["warnings"].append(f"Step {i}: observation out of bounds")

            if terminated or truncated:
                games_completed += 1
                obs, info = env.reset()

        except Exception as e:
            errors_in_step += 1
            if errors_in_step <= 3:
                result["errors"].append(f"Step {i} error: {e}")
            if errors_in_step >= 5:
                result["valid"] = False
                result["errors"].append("Too many step errors, aborting")
                break

    result["stats"]["games_completed"] = games_completed
    result["stats"]["steps_run"] = min(num_steps, num_steps)
    result["stats"]["step_errors"] = errors_in_step

    if errors_in_step > 0:
        result["valid"] = False

    # 5. config 검증
    config = env.config
    if config.total_spaces == 0:
        result["errors"].append("Board has 0 spaces")
        result["valid"] = False

    buyable = [s for s in config.spaces if s.is_buyable]
    if len(buyable) == 0:
        result["warnings"].append("No buyable properties on the board")

    result["stats"]["total_spaces"] = config.total_spaces
    result["stats"]["buyable_spaces"] = len(buyable)
    result["stats"]["starting_money"] = config.starting_money

    return result
