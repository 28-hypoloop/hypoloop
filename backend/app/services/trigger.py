import os
from pathlib import Path

import httpx

from app.core.path_utils import get_hypothesis_yml_path
from app.services.yml_generator import set_hypothesis_ready

# Set AGENT_TRIGGER_URL env var to enable HTTP agent notification after ready flag is set.
AGENT_TRIGGER_URL = os.getenv("AGENT_TRIGGER_URL", "")


def set_ready(*, project_id: str, u_id: str, hypothesis_id: str) -> Path:
    """
    Set ready=true in the hypothesis YML, then notify the agent via HTTP if
    AGENT_TRIGGER_URL is configured. Returns the path of the modified YML file.
    Raises FileNotFoundError if the hypothesis YML does not exist yet.
    """
    yml_path = get_hypothesis_yml_path(project_id, u_id, hypothesis_id)
    if not yml_path.exists():
        raise FileNotFoundError(f"Hypothesis YML not found: {yml_path}")

    set_hypothesis_ready(yml_path)

    if AGENT_TRIGGER_URL:
        _notify_agent(hypothesis_id=hypothesis_id, yml_path=str(yml_path))

    return yml_path


def _notify_agent(*, hypothesis_id: str, yml_path: str) -> None:
    """POST trigger payload to the agent server. Errors are logged but not raised."""
    payload = {"hypothesis_id": hypothesis_id, "yml_path": yml_path}
    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(AGENT_TRIGGER_URL, json=payload)
    except httpx.HTTPError:
        pass  # agent notification is best-effort; the yml ready flag is already set
