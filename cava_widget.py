import subprocess
import os
from textual.widgets import Static
from textual import work
from textual.reactive import reactive
from rich.text import Text
from logger import logger

class CavaWidget(Static):
    bars = reactive([])

    def __init__(self, num_bars=16, **kwargs):
        super().__init__(**kwargs)
        self.num_bars = num_bars
        self.cava_process = None
        self.config_path = "/tmp/ym-cli-cava.conf"

    def on_mount(self):
        logger.info("CavaWidget mounted")
        self.create_cava_config()
        self.run_cava()

    def create_cava_config(self):
        config = f"""
[general]
bars = {self.num_bars}
sleep_timer = 0
[input]
method = pulse
source = auto
[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = 15
"""
        with open(self.config_path, "w") as f:
            f.write(config)

    @work(exclusive=True, thread=True)
    def run_cava(self):
        logger.info("Starting Cava subprocess")
        self.cava_process = subprocess.Popen(
            ["cava", "-p", self.config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )

        for line in self.cava_process.stdout:
            if not line.strip():
                continue
            try:
                values = [int(v) for v in line.strip().split(';') if v]
                if values:
                    self.bars = values
            except ValueError:
                continue

    def render(self):
        if not self.bars:
            return Text(" " * self.num_bars)
        
        # Block characters with more levels (16 levels now)
        chars = [" ", " ", "▂", "▂", "▃", "▃", "▄", "▄", "▅", "▅", "▆", "▆", "▇", "▇", "█", "█"]
        output = ""
        for val in self.bars:
            idx = min(val, len(chars) - 1)
            output += chars[idx]
        
        return Text(output, style="cyan")

    def on_unmount(self):
        logger.info("CavaWidget unmounting")
        if self.cava_process:
            self.cava_process.terminate()
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
