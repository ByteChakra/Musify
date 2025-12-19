import os
os.environ['KIVY_AUDIO'] = 'ffpyplayer'

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem, MDNavigationItemIcon, MDNavigationItemLabel
from kivy.core.window import Window
from kivy.properties import StringProperty

from core.audio_player import AudioPlayer
from core.music_service import MusicService
from ui.screens.home import HomeScreen
from ui.screens.search import SearchScreen
from ui.screens.player import PlayerScreen

Window.size = (360, 640)

class MusifyApp(MDApp):
    def build(self):
        self.audio_player = AudioPlayer()
        self.audio_player.set_on_complete_callback(self.play_next)
        self.music_service = MusicService()
        
        self.queue = []
        self.current_index = -1
        self.shuffle_mode = False
        self.repeat_mode = False
        self.current_playback_req_id = 0
        
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        
        # Root Layout
        self.root_layout = MDBoxLayout(orientation='vertical')
        
        # Screen Manager
        self.screen_manager = MDScreenManager()
        
        # Initialize Screens
        self.home_screen = HomeScreen(name='home')
        self.search_screen = SearchScreen(name='search')
        self.player_screen = PlayerScreen(name='player')
        
        self.screen_manager.add_widget(self.home_screen)
        self.screen_manager.add_widget(self.search_screen)
        self.screen_manager.add_widget(self.player_screen)
        
        self.root_layout.add_widget(self.screen_manager)
        
        # Navigation Bar
        self.nav_bar = MDNavigationBar(
            on_switch_tabs=self.on_switch_tabs
        )
        
        # Items
        # Home
        self.item_home = MDNavigationItem(
            MDNavigationItemIcon(icon="home"),
            MDNavigationItemLabel(text="Home"),
        )
        self.item_home.name = "home"
        self.nav_bar.add_widget(self.item_home)

        # Search
        self.item_search = MDNavigationItem(
            MDNavigationItemIcon(icon="magnify"),
            MDNavigationItemLabel(text="Search"),
        )
        self.item_search.name = "search"
        self.nav_bar.add_widget(self.item_search)

        # Player
        self.item_player = MDNavigationItem(
            MDNavigationItemIcon(icon="music-circle"),
            MDNavigationItemLabel(text="Player"),
        )
        self.item_player.name = "player"
        self.nav_bar.add_widget(self.item_player)
        
        self.root_layout.add_widget(self.nav_bar)
        
        return self.root_layout

    def on_switch_tabs(self, bar, item, item_icon, item_text):
        self.screen_manager.current = item.name

    def start_playback(self, title, artist, thumbnail):
        """Internal method to update UI and start playing the current song in queue."""
        # Switch to Player Tab (visual only, we need to update Nav Bar state ideally)
        self.screen_manager.current = 'player'
        # Note: Updating Nav Bar active state programmatically in 2.0 can be tricky, 
        # usually assume user clicks. We'll skip forcing visual nav bar update for now to avoid crashes.
        
        # Update Player Screen Logic
        self.player_screen.title = title
        self.player_screen.artist = artist
        self.player_screen.thumbnail = thumbnail
        
        print(f"Playing {title} by {artist}")
        # Real streaming logic here...
        
        # Update Recently Played
        self.home_screen.add_recently_played(title, artist, thumbnail, video_id)

    def play_song(self, title, artist, thumbnail, video_id=None):
        # Legacy support or single song play
        self.play_list([{'title': title, 'artist': artist, 'thumbnail': thumbnail, 'videoId': video_id}], 0)

    
    def play_list(self, songs, start_index=0):
        normalized_queue = []
        for song in songs:
             # Check if it's already normalized or raw
             if 'videoId' in song: # Raw API style
                  title = song.get('title', 'Unknown')
                  video_id = song['videoId']
                  # Handle artist list or string
                  a_data = song.get('artists', [])
                  if isinstance(a_data, list) and a_data:
                      artist = a_data[0]['name']
                  else:
                      artist = "Unknown"
                  
                  thumbs = song.get('thumbnails', [])
                  thumb = thumbs[-1]['url'] if thumbs else ""
                  normalized_queue.append({
                      'title': title, 
                      'artist': artist, 
                      'thumbnail': thumb,
                      'videoId': video_id
                  })
             elif 'thumbnails' in song and 'videoId' not in song: 
                 # Edge case: some search results might not have videoId if they are playlists/albums
                 # But typically songs have it. If missing, we might skip or try to use what we have.
                 pass
             else:
                 # Assume already normalized
                 normalized_queue.append(song)
        
        self.queue = normalized_queue
        self.current_index = start_index
        
        if 0 <= start_index < len(self.queue):
            item = self.queue[start_index]
            self.start_playback(item.get('title'), item.get('artist'), item.get('thumbnail'), item.get('videoId'))

    def start_playback(self, title, artist, thumbnail, video_id=None):
        """Async playback start."""
        # Switch to Player Tab
        self.screen_manager.current = 'player'
        
        # Update Player Screen Logic
        self.player_screen.title = title
        self.player_screen.artist = artist
        self.player_screen.thumbnail = thumbnail
        
        print(f"Playing {title} by {artist} (ID: {video_id})")
        
        if video_id:
            import threading
            self.current_playback_req_id += 1
            req_id = self.current_playback_req_id
            threading.Thread(target=self._fetch_and_play, args=(video_id, req_id)).start()
        else:
            print("No video ID provided for playback.")

    def _fetch_and_play(self, video_id, req_id):
        if req_id != self.current_playback_req_id:
            return

        print(f"Downloading stream for {video_id}...")
        file_path = self.music_service.get_audio_path(video_id)

        if req_id != self.current_playback_req_id:
            return

        if file_path:
            import os
            print(f"Playing locally from: {file_path}")
            # Ensure path separation is correct/normalized for Windows
            file_path = os.path.normpath(file_path)
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.audio_player.play(file_path))
        else:
            print(f"Could not download audio for {video_id}")


    def play_next(self):
        if not self.queue:
            return

        if self.repeat_mode:
            song = self.queue[self.current_index]
            self.start_playback(song.get('title'), song.get('artist'), song.get('thumbnail'), song.get('videoId'))
            return

        next_index = self.current_index + 1
        
        if self.shuffle_mode:
            import random
            next_index = random.randint(0, len(self.queue) - 1)
        
        if next_index < len(self.queue):
            self.current_index = next_index
            song = self.queue[self.current_index]
            self.start_playback(song.get('title'), song.get('artist'), song.get('thumbnail'), song.get('videoId'))
        else:
            print("Queue finished")

    def play_previous(self):
        if not self.queue:
            return
            
        prev_index = self.current_index - 1
        if prev_index >= 0:
            self.current_index = prev_index
            song = self.queue[self.current_index]
            self.start_playback(song.get('title'), song.get('artist'), song.get('thumbnail'), song.get('videoId'))
        else:
            song = self.queue[self.current_index]
            self.start_playback(song.get('title'), song.get('artist'), song.get('thumbnail'), song.get('videoId'))

    def toggle_shuffle(self):
        self.shuffle_mode = not self.shuffle_mode
        print(f"Shuffle: {self.shuffle_mode}")
        return self.shuffle_mode

    def toggle_repeat(self):
        self.repeat_mode = not self.repeat_mode
        print(f"Repeat: {self.repeat_mode}")
        return self.repeat_mode

if __name__ == "__main__":
    MusifyApp().run()
