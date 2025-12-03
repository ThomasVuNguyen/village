import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "uid": "",
    "password": "",
    "apps": [],
    "firebase_url": "",
    "api_key": "",
}


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    merged = DEFAULT_CONFIG.copy()
    merged.update(data or {})
    return merged


def save_config(cfg: Dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def set_value(key: str, value: Any) -> Dict[str, Any]:
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    return cfg


def machine_identity(cfg: Dict[str, Any]) -> Dict[str, str]:
    return {"uid": cfg.get("uid", ""), "password": cfg.get("password", "")}
