import logging
import os
import subprocess
from pathlib import Path

from app.core.path_utils import get_hypothesis_yml_path
from app.services.yml_generator import set_hypothesis_ready

logger = logging.getLogger(__name__)


def set_ready(*, project_id: str, u_id: str, hypothesis_id: str) -> Path:
    """
    Set ready=true in the hypothesis YML, then launch the agent runner as a
    background subprocess. Returns the path of the modified YML file.
    Raises FileNotFoundError if the hypothesis YML does not exist yet.
    """
    yml_path = get_hypothesis_yml_path(project_id, u_id, hypothesis_id)
    if not yml_path.exists():
        raise FileNotFoundError(f"Hypothesis YML not found: {yml_path}")

    set_hypothesis_ready(yml_path)
    _notify_agent(project_id=project_id, u_id=u_id, hypothesis_id=hypothesis_id)
    return yml_path


def _notify_agent(*, project_id: str, u_id: str, hypothesis_id: str) -> None:
    """Launch agent/src/runner.py as a detached background process."""
    runner_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "agent", "src", "runner.py")
    )
    cwd_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    subprocess.Popen(
        [
            "python", runner_path,
            "--project_id", project_id,
            "--hypothesis_id", hypothesis_id,
            "--u_id", u_id,
        ],
        cwd=cwd_path,
        env=env,
    )
    logger.info(
        "Launched agent runner for hypothesis %s (project=%s)", hypothesis_id, project_id
    )
