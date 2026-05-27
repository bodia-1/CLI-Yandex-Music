from yandex_music import Client
import config
from logger import logger

class YandexBackend:
    def __init__(self):
        self.client = None
        self.token = config.get_token()

    def init_client(self):
        if not self.token:
            logger.error("No token found in config")
            return False
        try:
            self.client = Client(self.token).init()
            logger.info("Yandex Client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Yandex Client: {e}")
            return False

    def get_liked_tracks(self):
        if not self.client:
            return []
        try:
            likes = self.client.users_likes_tracks()
            tracks = likes.fetch_tracks()
            logger.info(f"Fetched {len(tracks)} liked tracks")
            return tracks
        except Exception as e:
            logger.error(f"Error fetching liked tracks: {e}")
            return []

    def search_tracks(self, query):
        if not self.client:
            return []
        try:
            search_result = self.client.search(query, type_="track")
            if search_result.tracks:
                logger.info(f"Search for '{query}' returned {len(search_result.tracks.results)} tracks")
                return search_result.tracks.results
            return []
        except Exception as e:
            logger.error(f"Error searching tracks for '{query}': {e}")
            return []

    def get_track_download_info(self, track_id):
        if not self.client:
            return None
        try:
            track = self.client.tracks([track_id])[0]
            info = track.get_download_info(get_direct_links=True)
            # Prefer higher bitrate
            info.sort(key=lambda x: x.bitrate_in_kbps, reverse=True)
            logger.info(f"Got download info for track {track_id}")
            return info[0].direct_link
        except Exception as e:
            logger.error(f"Error getting download info for track {track_id}: {e}")
            return None

    def like_track(self, track_id):
        if not self.client: return False
        try:
            self.client.users_likes_tracks_add(track_id)
            logger.info(f"Liked track {track_id}")
            return True
        except Exception as e:
            logger.error(f"Error liking track {track_id}: {e}")
            return False

    def unlike_track(self, track_id):
        if not self.client: return False
        try:
            self.client.users_likes_tracks_remove(track_id)
            logger.info(f"Unliked track {track_id}")
            return True
        except Exception as e:
            logger.error(f"Error unliking track {track_id}: {e}")
            return False
