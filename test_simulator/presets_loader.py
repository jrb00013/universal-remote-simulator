"""
Load presets and time_rules from autonomous_config.json for API and scheduler.
"""
import json
import os
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "autonomous_config.json")


def load_autonomous_config(path: str = None) -> Dict[str, Any]:
    p = path or os.environ.get("AUTONOMOUS_CONFIG") or DEFAULT_CONFIG_PATH
    if not os.path.isfile(p):
        return {"presets": [], "time_rules": [], "default_target": "simulator"}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def get_presets(path: str = None) -> List[Dict[str, Any]]:
    return load_autonomous_config(path).get("presets", [])


def get_preset_by_name(name: str, path: str = None) -> Optional[Dict[str, Any]]:
    for p in get_presets(path):
        if p.get("name") == name:
            return p
    return None


def get_time_rules(path: str = None) -> List[Dict[str, Any]]:
    return load_autonomous_config(path).get("time_rules", [])
