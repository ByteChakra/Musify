from core.music_service import MusicService
import json

def debug_structure():
    service = MusicService()
    query = "Tum Hi Ho"
    print(f"Searching for '{query}'...")
    songs = service.search_songs(query)
    
    if songs:
        print(f"Got {len(songs)} songs.")
        s = songs[0] # The first one is likely what they clicked
        print("First song keys:", s.keys())
        print("First song full dump:")
        print(json.dumps(s, indent=2))
        
        # Check specifically for videoId
        print(f"videoId: {s.get('videoId')}")
    else:
        print("No songs returned.")

if __name__ == "__main__":
    debug_structure()
