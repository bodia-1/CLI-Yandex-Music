import subprocess
import json
import socket
import os
import time

class Player:
    def __init__(self):
        self.mpv_process = None
        self.socket_path = "/tmp/ym-cli-mpv.sock"

    def start(self):
        if self.mpv_process:
            self.stop()
        
        # Start mpv in idle mode with IPC enabled
        self.mpv_process = subprocess.Popen(
            ["mpv", "--idle", "--no-video", f"--input-ipc-server={self.socket_path}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Give it a moment to start the socket
        time.sleep(0.5)

    def stop(self):
        if self.mpv_process:
            self.mpv_process.terminate()
            self.mpv_process = None
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

    def _send_command(self, command):
        if not os.path.exists(self.socket_path):
            return None
        
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(self.socket_path)
                msg = json.dumps({"command": command}) + "\n"
                s.sendall(msg.encode())
                # We don't necessarily need the response for simple commands
                # but we could read it if needed.
        except Exception:
            pass

    def play_url(self, url):
        self._send_command(["loadfile", url, "replace"])

    def toggle_pause(self):
        self._send_command(["cycle", "pause"])

    def set_volume(self, value):
        # value 0-100
        self._send_command(["set_property", "volume", value])

    def seek(self, seconds):
        self._send_command(["seek", seconds, "relative"])
