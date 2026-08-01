"""Command builders for the ReBotArm platform profile."""

import os
from pathlib import Path

from backend.models.recording import RecordingRequest


APP_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REBOT_ROOT = APP_ROOT / "hardware" / "rebotarm" / "rebot_datacollect"


def rebotarm_enabled(config) -> bool:
    """Return whether the current config should use the ReBotArm command path."""
    profile = os.environ.get("KAIRO_ROBOT_PROFILE", "rebotarm").lower()
    return config.mode == "single" and profile in {"rebotarm", "auto"}


def _rebot_root() -> Path:
    return Path(os.environ.get("REBOT_DATACOLLECT_ROOT", DEFAULT_REBOT_ROOT)).expanduser()


def _single_arm_env(config) -> dict[str, str]:
    sa = config.single_arm
    env = {
        "PY": os.environ.get("LEROBOT_PYTHON", os.environ.get("PY", "python")),
        "CAN": sa.follower_port or os.environ.get("CAN", "can0"),
        "LEADER_PORT": sa.leader_port or os.environ.get("LEADER_PORT", "/dev/ttyCH341USB0"),
    }

    if sa.cameras:
        front = sa.cameras[0]
        env["FRONT_CAM"] = str(front.index)

    env.setdefault("WRIST_CAM", os.environ.get("WRIST_CAM", "CV275610002L"))
    env.setdefault("NO_DEPTH", os.environ.get("NO_DEPTH", "0"))
    env.setdefault("NONBLOCK", os.environ.get("NONBLOCK", "1"))
    env.setdefault("DEPTH_PRESET", os.environ.get("DEPTH_PRESET", "ultrafast"))
    return env


def build_rebotarm_teleop_command(config) -> tuple[list[str], dict[str, str]]:
    """Build the ReBotArm teleoperation subprocess command and env."""
    script = _rebot_root() / "scripts" / "teleop_rebot.sh"
    return ["bash", str(script)], _single_arm_env(config)


def build_rebotarm_record_command(config, request: RecordingRequest) -> tuple[list[str], dict[str, str]]:
    """Build the ReBotArm dataset recording subprocess command and env."""
    script = _rebot_root() / "scripts" / "record_rebot.sh"
    env = _single_arm_env(config)
    env.update(
        {
            "REPO_ID": request.repo_id,
            "TASK": request.single_task,
            "EPISODES": str(request.num_episodes),
            "PUSH": os.environ.get("PUSH", "false"),
            "NO_DISPLAY": "0" if request.display_data else "1",
        }
    )
    return ["bash", str(script), f"--dataset.episode_time_s={request.episode_time_s}", f"--dataset.reset_time_s={request.reset_time_s}"], env
