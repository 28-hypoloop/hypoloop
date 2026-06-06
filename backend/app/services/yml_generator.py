from pathlib import Path

import yaml

from app.core.path_utils import ensure_dir, get_hypothesis_yml_path


def generate_hypothesis_yml(
    *,
    u_id: str,
    project_id: str,
    hypothesis_id: str,
    content: str,
    max_experiments: int,
    parallel_count: int,
) -> Path:
    """
    Write the hypothesis YML file (u_id_hypothesis_id.yml) to the hypothesis directory.
    Sets ready=false; call set_hypothesis_ready() after triggering.
    Returns the path of the written file.
    """
    data = {
        "u_id": u_id,
        "project_id": project_id,
        "hypothesis_id": hypothesis_id,
        "content": content,
        "max_experiments": max_experiments,
        "parallel_count": parallel_count,
        "ready": False,
    }
    yml_path = get_hypothesis_yml_path(project_id, u_id, hypothesis_id)
    ensure_dir(yml_path.parent)
    _write_yml(yml_path, data)
    return yml_path


def set_hypothesis_ready(yml_path: Path) -> None:
    """Flip ready=true in an existing hypothesis YML file."""
    data = read_hypothesis_yml(yml_path)
    data["ready"] = True
    _write_yml(yml_path, data)


def read_hypothesis_yml(yml_path: Path) -> dict:
    """Read and return the contents of a hypothesis YML file."""
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _write_yml(path: Path, data: dict) -> None:
    """Overwrite a YML file with the given data dict."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
