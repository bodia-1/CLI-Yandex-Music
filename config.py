import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "yandex-music-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_token():
    return load_config().get("token")

def set_token(token):
    config = load_config()
    config["token"] = token
    save_config(config)
