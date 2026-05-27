# CLI Yandex Music with Cava

A modern, high-performance terminal interface for Yandex Music with real-time audio visualization.

![License](https://img.shields.io/github/license/bodia-1/CLI-Yandex-Music)

## Features
- **Modern TUI**: Built with Python and the Textual framework.
- **Embedded Cava**: Real-time frequency visualizer integrated into the dashboard.
- **Auto-Next**: Automatically plays the next track in the list.
- **Like/Unlike**: Heart tracks directly from the terminal (Shortcut: `L`).
- **Gallery View**: Browse your Liked Tracks or search the entire Yandex catalog.
- **Custom Themes**: Configurable colors and styles (stored in `config.json`).
- **Robust Logging**: Diagnoses problems instantly via `app.log`.

## Installation

### Prerequisites
- **Python 3.8+**
- **mpv**: For high-quality audio playback.
- **cava**: For audio visualization.
- **PulseAudio**: (Standard on most Linux distros) for audio capture.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/bodia-1/CLI-Yandex-Music.git
   cd CLI-Yandex-Music
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install textual yandex-music requests
   ```

## Usage

### 1. Authentication
Run the authentication script to link your Yandex account:
```bash
python auth.py
```
Follow the link provided and enter the code in your browser.

### 2. Launch
Start the player:
```bash
python main.py
```

### Keyboard Shortcuts
- `Space`: Play/Pause
- `N`: Next Track
- `P`: Previous Track
- `L`: Like/Unlike current track
- `Q`: Quit

## Configuration
Themes and tokens are stored in `~/.config/yandex-music-cli/config.json`.
Logs are available at `~/.config/yandex-music-cli/app.log`.

## License
MIT
