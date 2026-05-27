from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, ListItem, ListView, Label, Static
from textual.containers import Container, Horizontal, Vertical
from textual import work
from yandex_backend import YandexBackend
from player import Player
from cava_widget import CavaWidget
import config

class YMApp(App):
    CSS = """
    Screen {
        background: #121212;
    }
    #main_layout {
        layout: horizontal;
    }
    #sidebar {
        width: 25;
        background: #181818;
        border-right: solid #333;
    }
    #content_area {
        width: 1fr;
    }
    #search_container {
        height: 3;
        margin: 1 0;
        display: none;
    }
    #search_container.visible {
        display: block;
    }
    #track_list {
        width: 100%;
        background: #1a1a1a;
    }
    #footer_controls {
        height: 5;
        background: #181818;
        border-top: solid #333;
        padding: 0 2;
    }
    .track-item {
        padding: 0 1;
    }
    #cava_visualizer {
        width: 32;
        height: 1;
        content-align: center middle;
    }
    .nav-item {
        padding: 1 2;
    }
    .nav-item:hover {
        background: #333;
    }
    .nav-selected {
        background: #222;
        color: #00ffff;
        text-style: bold;
    }
    """

    def __init__(self):
        super().__init__()
        self.backend = YandexBackend()
        self.player = Player()
        self.current_tracks = []
        self.current_view = "search"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            ListView(
                ListItem(Label(" Search", classes="nav-item"), id="nav_search"),
                ListItem(Label(" Liked Tracks", classes="nav-item"), id="nav_liked"),
                id="sidebar"
            ),
            Vertical(
                Horizontal(
                    Input(placeholder="Search for tracks...", id="search_input"),
                    id="search_container",
                    classes="visible"
                ),
                ListView(id="track_list"),
                id="content_area"
            ),
            id="main_layout"
        )
        yield Horizontal(
            Vertical(
                Label("Not playing", id="current_track_label"),
                Horizontal(
                    Label("Vol: 100%", id="volume_label"),
                    CavaWidget(num_bars=32, id="cava_visualizer"),
                ),
                id="playback_info"
            ),
            id="footer_controls"
        )
        yield Footer()

    def on_mount(self):
        if not self.backend.init_client():
            self.notify("No token found. Please run auth.py first", severity="error")
        self.player.start()

    def on_unmount(self):
        self.player.stop()

    async def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "search_input":
            query = event.value
            if query:
                self.run_search(query)

    @work(exclusive=True)
    async def run_search(self, query):
        tracks = self.backend.search_tracks(query)
        self.current_tracks = tracks
        
        track_list = self.query_one("#track_list", ListView)
        await track_list.clear()
        
        for track in tracks:
            artists = ", ".join(a.name for a in track.artists)
            label = f"{track.title} - {artists}"
            track_list.append(ListItem(Label(label, classes="track-item")))

    async def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.id == "sidebar":
            item_id = event.item.id
            if item_id == "nav_search":
                self.switch_to_search()
            elif item_id == "nav_liked":
                self.switch_to_liked()
        elif event.list_view.id == "track_list":
            idx = event.list_view.index
            if idx is not None and idx < len(self.current_tracks):
                track = self.current_tracks[idx]
                self.play_track(track)

    def switch_to_search(self):
        self.current_view = "search"
        self.query_one("#search_container").add_class("visible")
        self.query_one("#track_list").clear()
        self.current_tracks = []

    def switch_to_liked(self):
        self.current_view = "liked"
        self.query_one("#search_container").remove_class("visible")
        self.load_liked_tracks()

    @work(exclusive=True)
    async def load_liked_tracks(self):
        self.notify("Loading liked tracks...")
        tracks = self.backend.get_liked_tracks()
        self.current_tracks = tracks
        
        track_list = self.query_one("#track_list", ListView)
        await track_list.clear()
        
        for track in tracks:
            artists = ", ".join(a.name for a in track.artists)
            label = f"{track.title} - {artists}"
            track_list.append(ListItem(Label(label, classes="track-item")))

    @work(exclusive=True)
    async def play_track(self, track):
        self.notify(f"Fetching link for {track.title}...")
        url = self.backend.get_track_download_info(track.id)
        if url:
            self.player.play_url(url)
            artists = ", ".join(a.name for a in track.artists)
            self.query_one("#current_track_label", Label).update(f"Playing: {track.title} - {artists}")
        else:
            self.notify("Failed to get download link", severity="error")

    def action_toggle_pause(self):
        self.player.toggle_pause()

    def action_quit(self):
        self.app.exit()

if __name__ == "__main__":
    app = YMApp()
    app.run()
