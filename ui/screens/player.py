from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from kivymd.uix.button import MDIconButton
from kivymd.uix.slider import MDSlider
from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.clock import Clock

class PlayerScreen(MDScreen):
    title = StringProperty("No Song Playing")
    artist = StringProperty("Unknown Artist")
    thumbnail = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding="20dp", spacing="20dp")
        
        # Album Art
        self.image_container = MDBoxLayout(size_hint=(None, None), size=("250dp", "250dp"), pos_hint={'center_x': 0.5})
        self.image = FitImage(source=self.thumbnail, radius=[20,])
        self.image_container.add_widget(self.image)
        self.layout.add_widget(self.image_container)
        
        # Song Info
        self.info_box = MDBoxLayout(orientation='vertical', size_hint_y=None, height="80dp", spacing="5dp")
        self.title_label = MDLabel(
            text=self.title, 
            halign="center", 
            theme_text_color="Primary", 
            font_style="Headline",
            role="small"
        )
        self.artist_label = MDLabel(
            text=self.artist, 
            halign="center", 
            theme_text_color="Secondary", 
            font_style="Title",
            role="medium"
        )
        self.info_box.add_widget(self.title_label)
        self.info_box.add_widget(self.artist_label)
        self.layout.add_widget(self.info_box)
        
        # Slider Container with Time Labels
        self.slider_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="40dp", padding=("20dp", 0))
        
        self.current_time_label = MDLabel(
            text="0:00", 
            halign="left", 
            theme_text_color="Secondary",
            font_style="Label",
            role="large",
            size_hint_x=None,
            width="40dp"
        )
        
        self.slider = MDSlider(min=0, max=100, value=0, size_hint_x=1)
        self.slider.bind(on_touch_up=self.on_slider_release)
        
        self.total_time_label = MDLabel(
            text="0:00", 
            halign="right", 
            theme_text_color="Secondary",
            font_style="Label",
            role="large",
            size_hint_x=None,
            width="40dp"
        )
        
        self.slider_box.add_widget(self.current_time_label)
        self.slider_box.add_widget(self.slider)
        self.slider_box.add_widget(self.total_time_label)
        
        self.layout.add_widget(self.slider_box)
        
        # Controls
        self.controls = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="80dp", spacing="10dp", padding="10dp")
        self.controls.pos_hint = {'center_x': 0.5}
        
        self.shuffle_btn = MDIconButton(icon="shuffle", font_size="24sp", on_release=self.toggle_shuffle)
        self.prev_btn = MDIconButton(icon="skip-previous", font_size="40sp", on_release=self.play_previous)
        self.play_btn = MDIconButton(
            icon="play-circle", 
            font_size="64sp", 
            theme_text_color="Custom", 
            text_color="green",
            on_release=self.toggle_play
        )
        self.next_btn = MDIconButton(icon="skip-next", font_size="40sp", on_release=self.play_next)
        self.repeat_btn = MDIconButton(icon="repeat", font_size="24sp", on_release=self.toggle_repeat)
        
        self.controls.add_widget(self.shuffle_btn)
        self.controls.add_widget(self.prev_btn)
        self.controls.add_widget(self.play_btn)
        self.controls.add_widget(self.next_btn)
        self.controls.add_widget(self.repeat_btn)
        
        self.layout.add_widget(self.controls)
        self.layout.add_widget(MDBoxLayout()) # Bottom spacer
        
        self.add_widget(self.layout)
        
        # Scheduling update
        self.update_event = Clock.schedule_interval(self.update_progress, 1)

    def format_time(self, seconds):
        if seconds < 0: return "0:00"
        m = int(seconds / 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"

    def update_progress(self, dt):
        app = MDApp.get_running_app()
        if hasattr(app, 'audio_player') and app.audio_player:
            player = app.audio_player
            if player.is_playing:
                current = player.get_time()
                total = player.get_length()
                
                self.current_time_label.text = self.format_time(current)
                self.total_time_label.text = self.format_time(total)
                
                if total > 0:
                    self.slider.max = total
                    # Only update value if user is NOT dragging? 
                    # MDSlider doesn't have easy 'is_dragging' property exposed simple way.
                    # Simplified: just update.
                    self.slider.value = current

    def on_slider_release(self, instance, touch):
        if instance.collide_point(*touch.pos):
            app = MDApp.get_running_app()
            if hasattr(app, 'audio_player') and app.audio_player:
                 app.audio_player.seek(instance.value)

    def on_title(self, instance, value):
        if self.title_label:
            self.title_label.text = value
    
    def on_artist(self, instance, value):
        if self.artist_label:
            self.artist_label.text = value

    def on_thumbnail(self, instance, value):
        if self.image:
            self.image.source = value

    def toggle_play(self, instance):
        app = MDApp.get_running_app()
        if hasattr(app, 'audio_player'):
            player = app.audio_player
            if player.is_playing:
                player.pause()
                self.play_btn.icon = "play-circle"
            else:
                player.resume()
                self.play_btn.icon = "pause-circle"

    def play_next(self, instance):
        app = MDApp.get_running_app()
        app.play_next()

    def play_previous(self, instance):
        app = MDApp.get_running_app()
        app.play_previous()

    def toggle_shuffle(self, instance):
        app = MDApp.get_running_app()
        is_shuffle = app.toggle_shuffle()
        self.shuffle_btn.text_color = "green" if is_shuffle else "white"
        self.shuffle_btn.theme_text_color = "Custom" if is_shuffle else "Primary"

    def toggle_repeat(self, instance):
        app = MDApp.get_running_app()
        is_repeat = app.toggle_repeat()
        self.repeat_btn.text_color = "green" if is_repeat else "white"
        self.repeat_btn.theme_text_color = "Custom" if is_repeat else "Primary"
