from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, ListItem, ListView, Label, Button
from textual.containers import Container, Horizontal, Vertical
from textual import work, on
from textual.binding import Binding
from yandex_backend import YandexBackend
from player import Player
from cava_widget import CavaWidget
from logger import logger
import config

class YMApp(App):
    BINDINGS = [
        Binding("space", "toggle_pause", "Play/Pause"),
        Binding("l", "toggle_like", "Like/Unlike"),
        Binding("q", "quit", "Quit"),
        Binding("n", "next_track", "Next"),
        Binding("p", "prev_track", "Prev"),
    ]

    def __init__(self):
        super().__init__()
        self.backend = YandexBackend()
        self.player = Player(on_track_end=self.handle_track_end)
        self.current_tracks = []
        self.current_track = None
        self.theme = config.get_theme()
        
    def get_css(self) -> str:
        t = self.theme
        return f"""
        Screen {{
            background: {t['background']};
        }}
        #main_layout {{
            layout: horizontal;
        }}
        #sidebar {{
            width: 30;
            background: {t['sidebar_bg']};
            border-right: solid #333;
        }}
        #content_area {{
            width: 1fr;
        }}
        #search_container {{
            height: 3;
            margin: 1 0;
            display: none;
        }}
        #search_container.visible {{
            display: block;
        }}
        #track_list {{
            width: 100%;
            background: {t['list_bg']};
        }}
        #footer_controls {{
            height: 6;
            background: {t['footer_bg']};
            border-top: solid #333;
            padding: 1 2;
        }}
        .track-item {{
            padding: 0 1;
        }}
        #cava_visualizer {{
            width: 26;
            height: 3;
            margin: 1 2;
        }}
        .nav-item {{
            padding: 1 2;
        }}
        .nav-item:hover {{
            background: #333;
        }}
        #now_playing_sidebar {{
            height: auto;
            border-bottom: solid #333;
            padding: 1;
            align: center middle;
        }}
        #like_button {{
            min-width: 4;
            height: 1;
            border: none;
            background: transparent;
            color: #555;
        }}
        #like_button.liked {{
            color: #ff0000;
        }}
        """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Vertical(
                    Label("NOW PLAYING", id="sidebar_title"),
                    CavaWidget(num_bars=26, id="cava_visualizer"),
                    id="now_playing_sidebar"
                ),
                ListView(
                    ListItem(Label(" Search", classes="nav-item"), id="nav_search"),
                    ListItem(Label(" Liked Tracks", classes="nav-item"), id="nav_liked"),
                    id="sidebar_nav"
                ),
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
                Horizontal(
                    Label("Not playing", id="current_track_label"),
                    Button("❤", id="like_button"),
                ),
                Label("Vol: 100%", id="volume_label"),
                id="playback_info"
            ),
            id="footer_controls"
        )
        yield Footer()

    def on_mount(self):
        logger.info("Application mounted")
        if not self.backend.init_client():
            self.notify("No token found. Please run auth.py first", severity="error")
        self.player.start()

    def on_unmount(self):
        logger.info("Application unmounting")
        self.player.stop()

    def handle_track_end(self):
        logger.info("Track ended naturally, triggering auto-next")
        self.call_after_refresh(self.action_next_track)

    @on(Input.Submitted, "#search_input")
    def on_search(self, event: Input.Submitted):
        if event.value:
            self.run_search(event.value)

    @work(exclusive=True)
    async def run_search(self, query):
        tracks = self.backend.search_tracks(query)
        self.current_tracks = tracks
        track_list = self.query_one("#track_list", ListView)
        await track_list.clear()
        for track in tracks:
            artists = ", ".join(a.name for a in track.artists)
            track_list.append(ListItem(Label(f"{track.title} - {artists}", classes="track-item")))

    @on(ListView.Selected, "#sidebar_nav")
    def on_nav_select(self, event: ListView.Selected):
        item_id = event.item.id
        if item_id == "nav_search":
            self.query_one("#search_container").add_class("visible")
            self.query_one("#track_list").clear()
            self.current_tracks = []
        elif item_id == "nav_liked":
            self.query_one("#search_container").remove_class("visible")
            self.load_liked_tracks()

    @work(exclusive=True)
    async def load_liked_tracks(self):
        tracks = self.backend.get_liked_tracks()
        self.current_tracks = tracks
        track_list = self.query_one("#track_list", ListView)
        await track_list.clear()
        for track in tracks:
            artists = ", ".join(a.name for a in track.artists)
            track_list.append(ListItem(Label(f"{track.title} - {artists}", classes="track-item")))

    @on(ListView.Selected, "#track_list")
    def on_track_select(self, event: ListView.Selected):
        idx = event.list_view.index
        if idx is not None and idx < len(self.current_tracks):
            self.play_track(self.current_tracks[idx])

    @work(exclusive=True)
    async def play_track(self, track):
        self.current_track = track
        url = self.backend.get_track_download_info(track.id)
        if url:
            self.player.play_url(url)
            artists = ", ".join(a.name for a in track.artists)
            self.query_one("#current_track_label").update(f"Playing: {track.title} - {artists}")
            # Update like button status
            # For simplicity, we assume if it's in Liked view, it's liked. 
            # In search view, we'd need to check, but let's just toggle for now.
            self.query_one("#like_button").remove_class("liked")
        else:
            self.notify("Failed to get download link", severity="error")

    def action_toggle_pause(self):
        self.player.toggle_pause()

    def action_next_track(self):
        track_list = self.query_one("#track_list", ListView)
        if track_list.index is not None and track_list.index < len(self.current_tracks) - 1:
            track_list.index += 1
            self.play_track(self.current_tracks[track_list.index])

    def action_prev_track(self):
        track_list = self.query_one("#track_list", ListView)
        if track_list.index is not None and track_list.index > 0:
            track_list.index -= 1
            self.play_track(self.current_tracks[track_list.index])

    def action_toggle_like(self):
        if self.current_track:
            btn = self.query_one("#like_button")
            if "liked" in btn.classes:
                if self.backend.unlike_track(self.current_track.id):
                    btn.remove_class("liked")
                    self.notify("Removed from Liked")
            else:
                if self.backend.like_track(self.current_track.id):
                    btn.add_class("liked")
                    self.notify("Added to Liked")

    @on(Button.Pressed, "#like_button")
    def on_like_press(self):
        self.action_toggle_like()

if __name__ == "__main__":
    app = YMApp()
    app.run()
