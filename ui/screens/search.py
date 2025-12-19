from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.app import MDApp
from kivy.clock import Clock
import threading

from core.music_service import MusicService
from ui.components.music_card import MusicCard

class SearchScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = MusicService()
        
        # Main Layout
        self.layout = MDBoxLayout(orientation='vertical', padding="10dp", spacing="10dp")
        
        # Search Bar Area
        search_box = MDBoxLayout(size_hint_y=None, height="60dp", spacing="10dp")
        self.search_field = MDTextField(
            hint_text="Search songs...",
            mode="outlined",
            size_hint_x=0.8,
            pos_hint={'center_y': 0.5},
            on_text_validate=self.do_search
        )
        search_box.add_widget(self.search_field)
        
        search_btn = MDIconButton(
            icon="magnify",
            pos_hint={'center_y': 0.5},
            on_release=self.do_search
        )
        search_box.add_widget(search_btn)
        
        self.layout.add_widget(search_box)
        
        # Results Area
        self.scroll = MDScrollView(size_hint=(1, 1))
        self.results_grid = MDGridLayout(cols=2, spacing="15dp", padding="10dp", size_hint_y=None)
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))
        
        self.scroll.add_widget(self.results_grid)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)

    def do_search(self, instance):
        query = self.search_field.text
        if query:
            threading.Thread(target=self.perform_search, args=(query,)).start()

    def perform_search(self, query):
        results = self.service.search_songs(query)
        Clock.schedule_once(lambda dt: self.update_results(results))

    def update_results(self, songs):
        self.results_grid.clear_widgets()
        
        if not songs:
            # Handle no results
            return

        for song in songs:
            title = song.get('title', 'Unknown')
            artist = song['artists'][0]['name'] if song.get('artists') else "Unknown"
            thumbnails = song.get('thumbnails', [])
            thumbnail_url = thumbnails[-1]['url'] if thumbnails else ""
            video_id = song.get('videoId')
            
            card = MusicCard(title=title, artist=artist, thumbnail=thumbnail_url)
            card.bind(on_release=lambda x, t=title, a=artist, u=thumbnail_url, v=video_id: self.play_song(t, a, u, v))
            self.results_grid.add_widget(card)

    def play_song(self, title, artist, thumbnail, video_id=None):
        app = MDApp.get_running_app()
        app.play_song(title, artist, thumbnail, video_id)
