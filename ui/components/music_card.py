from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.fitimage import FitImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty

class MusicCard(MDCard):
    title = StringProperty("")
    artist = StringProperty("")
    thumbnail = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_behavior = True
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = ("140dp", "180dp")
        self.radius = [12, ]
        self.elevation = 4
        
        # Image Container
        self.image_box = MDBoxLayout(size_hint_y=0.7)
        self.image = FitImage(source=self.thumbnail, radius=[12, 12, 0, 0])
        self.image_box.add_widget(self.image)
        self.add_widget(self.image_box)
        
        # Text Container
        self.text_box = MDBoxLayout(orientation="vertical", size_hint_y=0.3, padding="8dp")
        self.title_label = MDLabel(
            text=self.title, 
            theme_text_color="Primary", 
            font_style="Title",
            role="small",
            shorten=True,
            shorten_from="right"
        )
        self.artist_label = MDLabel(
            text=self.artist, 
            theme_text_color="Secondary", 
            font_style="Label",
            role="small",
            shorten=True,
            shorten_from="right"
        )
        self.text_box.add_widget(self.title_label)
        self.text_box.add_widget(self.artist_label)
        self.add_widget(self.text_box)
    
    def on_thumbnail(self, instance, value):
        if hasattr(self, 'image'):
            self.image.source = value

    def on_title(self, instance, value):
        if hasattr(self, 'title_label'):
            self.title_label.text = value
        
    def on_artist(self, instance, value):
        if hasattr(self, 'artist_label'):
            self.artist_label.text = value
