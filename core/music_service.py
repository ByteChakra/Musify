from ytmusicapi import YTMusic

class MusicService:
    def __init__(self):
        self.yt = YTMusic()

    def get_trending(self):
        """Fetches trending songs from YouTube Music."""
        songs = []
        try:
            # Try official charts first
            results = self.yt.get_charts(country='US')
            if 'songs' in results and results['songs'].get('items'):
                songs = results['songs']['items']
            elif 'trending' in results and results['trending'].get('items'):
                songs = results['trending']['items']
        except Exception as e:
            print(f"Error fetching charts: {e}")
            
        if not songs:
            try:
                print("Fallback to search for trending songs...")
                songs = self.yt.search("trending", filter="songs", limit=20)
            except Exception as e:
                print(f"Error fetching trending fallback: {e}")
                
        return songs

    def search_songs(self, query):
        """Searches for songs."""
        try:
            return self.yt.search(query, filter='songs')
        except Exception as e:
            print(f"Error searching songs: {e}")
            return []

    def get_audio_path(self, video_id):
        """
        Downloads the audio using yt-dlp and returns the local file path.
        """
        import yt_dlp
        import os
        
        # Create cache directory
        cache_dir = os.path.join(os.getcwd(), 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Output template
        out_tmpl = os.path.join(cache_dir, '%(id)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/best',
            'outtmpl': out_tmpl,
            'quiet': True,
            'no_warnings': True,
            # 'overwrites': False, # Avoid re-downloading if possible, but proper check is safer
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Check if file already exists roughly (optional optimization)
                # For now, let yt-dlp handle it or force getting info first.
                
                # We can handle full URLs or just IDs.
                if "youtube.com" not in video_id and "youtu.be" not in video_id:
                    url = f"https://www.youtube.com/watch?v={video_id}"
                else:
                    url = video_id
                
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return os.path.abspath(filename)
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None
