from core.music_service import MusicService
import json

def verify_fix():
    print("Initializing MusicService...")
    service = MusicService()
    
    print("Calling get_trending()...")
    songs = service.get_trending()
    
    print(f"Fetched {len(songs)} songs.")
    if songs:
        print("First song sample:")
        print(json.dumps(songs[0], indent=2))
        
        # Verify critical keys presence for UI
        s = songs[0]
        # Check title
        if 'title' not in s:
             print("WARNING: 'title' missing")
        
        # Check videoId
        if 'videoId' not in s:
             print("WARNING: 'videoId' missing")
             
        # Check thumbnails
        if 'thumbnails' not in s:
             print("WARNING: 'thumbnails' missing")
             
    else:
        print("ERROR: No songs returned.")

if __name__ == "__main__":
    verify_fix()
