# CLI Yandex Music (Stable Version)

A clean, minimalist terminal interface for Yandex Music with integrated audio visualization. This version is kept stable for performance and aesthetics.

## Features
- **Minimalist TUI**: Simple and clean layout.
- **Embedded Cava**: Real-time frequency visualizer.
- **Search**: Search the entire Yandex catalog.
- **Liked Tracks**: Browse your favorites.

## Installation

### Prerequisites
- **Python 3.8+**
- **mpv**: For playback.
- **cava**: For visualization.

### Setup
1. Clone and enter directory:
   ```bash
   git clone https://github.com/bodia-1/CLI-Yandex-Music.git
   cd CLI-Yandex-Music
   git checkout stable
   ```
2. Setup environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install textual yandex-music requests
   ```

## Usage
1. Authenticate: `python auth.py`
2. Run: `python main.py`

## License
MIT
