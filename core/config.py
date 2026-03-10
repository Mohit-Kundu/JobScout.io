"""Configuration loading. Supports YAML (preferred) and JSON."""

import json
from pathlib import Path
from typing import Any

try:
    import yaml
    _HAS_YAML = True
except ModuleNotFoundError:
    _HAS_YAML = False

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.yaml"


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load scraper config from YAML."""
    path = config_path or DEFAULT_CONFIG_PATH
    path = Path(path)
    if not path.is_absolute():
        path = path if path.exists() else CONFIG_DIR / path.name
    if path.suffix.lower() in (".yaml", ".yml") and not _HAS_YAML:
        raise ModuleNotFoundError(
            "No module named 'yaml'. Install PyYAML: pip install PyYAML"
        )
    with open(path, encoding="utf-8") as f:
        text = f.read()
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    if suffix == ".json":
        return json.loads(text)
    return json.loads(text)
