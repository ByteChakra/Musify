from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.app import MDApp
from kivy.clock import Clock
import threading

from core.music_service import MusicService
from ui.components.music_card import MusicCard

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = MusicService()
        self.data_loaded = False
        
        # Main Layout
        self.main_scroll = MDScrollView(do_scroll_x=False, do_scroll_y=True)
        self.layout = MDBoxLayout(orientation='vertical', padding="10dp", spacing="10dp", size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        self.main_scroll.add_widget(self.layout)
        
        # --- Recently Played Section ---
        self.layout.add_widget(MDLabel(
            text="Recently Played", 
            font_style="Headline", 
            role="small",
            theme_text_color="Primary",
            size_hint_y=None, 
            height="40dp"
        ))
        
        self.recent_scroll = MDScrollView(size_hint=(1, None), height="200dp", do_scroll_x=True, do_scroll_y=False)
        self.recent_grid = MDGridLayout(rows=1, spacing="15dp", padding="10dp", size_hint_x=None, height="200dp")
        self.recent_grid.bind(minimum_width=self.recent_grid.setter('width'))
        self.recent_scroll.add_widget(self.recent_grid)
        self.layout.add_widget(self.recent_scroll)
        
        # --- Trending Section ---
        self.layout.add_widget(MDLabel(
            text="Trending Now", 
            font_style="Headline", 
            role="small",
            theme_text_color="Primary",
            size_hint_y=None, 
            height="40dp"
        ))
        
        self.trending_scroll = MDScrollView(size_hint=(1, None), height="200dp", do_scroll_x=True, do_scroll_y=False)
        self.trending_grid = MDGridLayout(rows=1, spacing="15dp", padding="10dp", size_hint_x=None, height="200dp")
        self.trending_grid.bind(minimum_width=self.trending_grid.setter('width'))
        self.trending_scroll.add_widget(self.trending_grid)
        self.layout.add_widget(self.trending_scroll)
        
        # Spinner
        self.spinner = MDCircularProgressIndicator(
            size_hint=(None, None), 
            size=("46dp", "46dp"), 
            pos_hint={'center_x': .5, 'center_y': .5},
            active=True
        )
        
        self.add_widget(self.main_scroll)
        self.add_widget(self.spinner)

        # Load recently played from file
        self.load_recently_played()
        
        # Trigger load immediately on startup (in a thread)
        Clock.schedule_once(lambda dt: threading.Thread(target=self.load_trending).start(), 1)

    def on_enter(self):
        # We can keep this just in case, or for re-fresh
        if not self.data_loaded:
             pass 
        self.refresh_recently_played()
    
    def load_recently_played(self):
        import json
        import os
        if os.path.exists("recently_played.json"):
            try:
                with open("recently_played.json", "r") as f:
                    self.recently_played_list = json.load(f)
            except Exception as e:
                print(f"Error loading recently played: {e}")
                self.recently_played_list = []
        else:
            self.recently_played_list = []

    def save_recently_played(self):
        import json
        try:
            with open("recently_played.json", "w") as f:
                json.dump(self.recently_played_list, f)
        except Exception as e:
            print(f"Error saving recently played: {e}")

    def load_trending(self):
        print("Loading trending songs...")
        # Fetch data
        try:
            trending_songs = self.service.get_trending()
            print(f"Fetched {len(trending_songs)} trending songs")
        except Exception as e:
            print(f"Error fetching trending in UI: {e}")
            trending_songs = []
            
        # Schedule UI update
        Clock.schedule_once(lambda dt: self.update_ui(trending_songs))

    def update_ui(self, songs):
        print(f"Updating UI with {len(songs)} songs")
        self.spinner.active = False
        self.remove_widget(self.spinner)
        
        if not songs:
            # Fallback for testing/offline
            songs = [
                {'title': 'Cartoon - On & On', 'artists': [{'name': 'Daniel Levi'}], 'thumbnails': [{'url': ''}], 'videoId': 'K4DyBUG242c'},
                {'title': 'Disfigure - Blank', 'artists': [{'name': 'NCS Release'}], 'thumbnails': [{'url': ''}], 'videoId': 'p7ZsBPK656s'},
                {'title': 'DEAF KEV - Invincible', 'artists': [{'name': 'NCS Release'}], 'thumbnails': [{'url': ''}], 'videoId': 'AOeY-nDp7hI'},
            ]

        for i, song in enumerate(songs):
            title = song.get('title', 'Unknown')
            artist = song['artists'][0]['name'] if song.get('artists') else "Unknown"
            thumbnails = song.get('thumbnails', [])
            thumbnail_url = thumbnails[-1]['url'] if thumbnails else ""
            video_id = song.get('videoId')
            
            # Ensure videoId is in the song dict for play_context
            if 'videoId' not in song and video_id:
                song['videoId'] = video_id

            card = MusicCard(title=title, artist=artist, thumbnail=thumbnail_url)
            # Pass the WHOLE songs list and the current index
            card.bind(on_release=lambda x, idx=i, s_list=songs: self.play_context(s_list, idx))
            self.trending_grid.add_widget(card)
        
        self.data_loaded = True

    def add_recently_played(self, title, artist, thumbnail, video_id=None):
        # Avoid duplicates or move to top
        song_data = {'title': title, 'artist': artist, 'thumbnail': thumbnail, 'videoId': video_id}
        
        # Remove if exists
        self.recently_played_list = [s for s in self.recently_played_list if s['title'] != title]
        # Insert at beginning
        self.recently_played_list.insert(0, song_data)
        
        # Limit to last 10
        if len(self.recently_played_list) > 10:
            self.recently_played_list.pop()
            
        self.save_recently_played()
        self.refresh_recently_played()

    def refresh_recently_played(self):
        self.recent_grid.clear_widgets()
        for song in self.recently_played_list:
            card = MusicCard(title=song['title'], artist=song['artist'], thumbnail=song['thumbnail'])
            card.bind(on_release=lambda x, t=song['title'], a=song['artist'], u=song['thumbnail'], v=song.get('videoId'): self.play_song(t, a, u, v))
            self.recent_grid.add_widget(card)

    def play_context(self, songs, index):
        app = MDApp.get_running_app()
        if hasattr(app, 'play_list'):
            app.play_list(songs, index)
        else:
            # Fallback
            song = songs[index]
            # ... normalize manual ...
            app.play_song(song['title'], "Artist", "")

    def play_song(self, title, artist, thumbnail, video_id=None):
        app = MDApp.get_running_app()
        app.play_song(title, artist, thumbnail, video_id)
