import subprocess
import json
import socket
import os
import time
import threading
from logger import logger

class Player:
    def __init__(self, on_track_end=None):
        self.mpv_process = None
        self.socket_path = "/tmp/ym-cli-mpv.sock"
        self.on_track_end = on_track_end
        self.monitor_thread = None
        self._stop_event = threading.Event()

    def start(self):
        if self.mpv_process:
            self.stop()

        logger.info("Starting mpv process")
        self.mpv_process = subprocess.Popen(
            ["mpv", "--idle", "--no-video", f"--input-ipc-server={self.socket_path}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(0.5)

        self._stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_ipc, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        logger.info("Stopping mpv process")
        self._stop_event.set()
        if self.mpv_process:
            self.mpv_process.terminate()
            self.mpv_process = None
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except Exception:
                pass

    def _monitor_ipc(self):
        while not self._stop_event.is_set():
            if not os.path.exists(self.socket_path):
                time.sleep(0.5)
                continue

            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.settimeout(1.0)
                    s.connect(self.socket_path)
                    logger.debug("Connected to mpv IPC socket")

                    while not self._stop_event.is_set():
                        try:
                            data = s.recv(4096)
                            if not data:
                                break

                            for line in data.decode().strip().split('\n'):
                                if not line: continue
                                try:
                                    event = json.loads(line)
                                    if event.get("event") == "end-file":
                                        reason = event.get("reason")
                                        logger.info(f"mpv event: end-file, reason: {reason}")
                                        if reason == "eof" and self.on_track_end:
                                            self.on_track_end()
                                except json.JSONDecodeError:
                                    continue
                        except socket.timeout:
                            continue
                        except Exception as e:
                            logger.error(f"Error reading from IPC socket: {e}")
                            break
            except Exception as e:
                logger.debug(f"IPC connection failed: {e}")
                time.sleep(1.0)

    def _send_command(self, command):
        if not os.path.exists(self.socket_path):
            return None

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(self.socket_path)
                msg = json.dumps({"command": command}) + "\n"
                s.sendall(msg.encode())
        except Exception as e:
            logger.error(f"Error sending command {command} to mpv: {e}")

    def play_url(self, url):
        logger.info(f"Playing URL: {url}")
        self._send_command(["loadfile", url, "replace"])

    def toggle_pause(self):
        logger.info("Toggling pause")
        self._send_command(["cycle", "pause"])

    def set_volume(self, value):
        logger.info(f"Setting volume to {value}")
        self._send_command(["set_property", "volume", value])

    def seek(self, seconds):
        logger.info(f"Seeking {seconds}s")
        self._send_command(["seek", seconds, "relative"])

