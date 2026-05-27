from yandex_music import Client
import config

class YandexBackend:
    def __init__(self):
        self.client = None
        self.token = config.get_token()

    def init_client(self):
        if not self.token:
            return False
        try:
            self.client = Client(self.token).init()
            return True
        except Exception:
            return False

    def get_liked_tracks(self):
        if not self.client:
            return []
        likes = self.client.users_likes_tracks()
        return likes.fetch_tracks()

    def search_tracks(self, query):
        if not self.client:
            return []
        search_result = self.client.search(query, type_="track")
        if search_result.tracks:
            return search_result.tracks.results
        return []

    def get_track_download_info(self, track_id):
        if not self.client:
            return None
        track = self.client.tracks([track_id])[0]
        info = track.get_download_info(get_direct_links=True)
        # Prefer higher bitrate
        info.sort(key=lambda x: x.bitrate_in_kbps, reverse=True)
        return info[0].direct_link
