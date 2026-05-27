import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "yandex-music-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_THEME = {
    "background": "#121212",
    "sidebar_bg": "#181818",
    "list_bg": "#1a1a1a",
    "accent": "#00ffff",
    "footer_bg": "#181818"
}

def load_config():
    if not CONFIG_FILE.exists():
        return {"theme": DEFAULT_THEME}
    with open(CONFIG_FILE, "r") as f:
        try:
            config = json.load(f)
            if "theme" not in config:
                config["theme"] = DEFAULT_THEME
            return config
        except json.JSONDecodeError:
            return {"theme": DEFAULT_THEME}

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

def get_theme():
    return load_config().get("theme", DEFAULT_THEME)

def set_theme(theme_dict):
    config = load_config()
    config["theme"] = theme_dict
    save_config(config)
