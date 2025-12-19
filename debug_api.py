from ytmusicapi import YTMusic
import json

yt = YTMusic()
try:
    print("Fetching charts...")
    results = yt.get_charts(country='US')
    print("Keys in result:", results.keys())
    if 'trending' in results:
        print("Keys in trending:", results['trending'].keys())
        items = results['trending'].get('items', [])
        print(f"Found {len(items)} items in trending")
        if items:
            print("First item sample:", json.dumps(items[0], indent=2))
    else:
        print("No 'trending' key found in results")
        print("Full dump:", json.dumps(results, indent=2))
except Exception as e:
    print(f"Error: {e}")
