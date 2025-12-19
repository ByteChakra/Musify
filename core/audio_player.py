from kivy.core.audio import SoundLoader
from kivy.clock import Clock

class AudioPlayer:
    def __init__(self):
        self.sound = None
        self.is_playing = False
        self.on_complete_callback = None

    def set_on_complete_callback(self, callback):
        self.on_complete_callback = callback

    def play(self, url):
        try:
            if self.sound:
                self.stop()
                self.sound.unload()
            
            self.sound = SoundLoader.load(url)
            if self.sound:
                self.sound.bind(on_stop=self._on_stop)
                self.sound.play()
                self.is_playing = True
                return True
            else:
                print("Failed to load sound")
                return False
        except Exception as e:
            print(f"Error in AudioPlayer.play: {e}")
            return False

    def _on_stop(self, instance):
        # Only trigger callback if we didn't manually stop/pause
        if self.is_playing: 
            self.is_playing = False
            if self.on_complete_callback:
                Clock.schedule_once(lambda dt: self.on_complete_callback())

    def stop(self):
        try:
            self.is_playing = False
            if self.sound:
                self.sound.stop()
                self.current_pos = 0 # Reset on full stop
        except Exception as e:
            print(f"Error in AudioPlayer.stop: {e}")

    def pause(self):
        self.is_playing = False
        if self.sound:
            self.current_pos = self.sound.get_pos()
            self.sound.stop()

    def resume(self):
        if self.sound:
            self.sound.play()
            if hasattr(self, 'current_pos') and self.current_pos > 0:
                self.sound.seek(self.current_pos)
            self.is_playing = True

    def get_time(self):
        if self.sound:
            return self.sound.get_pos()
        return 0

    def get_length(self):
        if self.sound:
            return self.sound.length
        return 0

    def seek(self, position):
        if self.sound:
            self.sound.seek(position)
            # update current_pos if paused
            if not self.is_playing:
                self.current_pos = position
