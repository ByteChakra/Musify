from ytmusicapi import YTMusic
import json

def test_trending():
    yt = YTMusic()
    output = {}
    
    try:
        print("Testing get_charts...")
        charts = yt.get_charts(country='US')
        print("get_charts success!")
        output['charts_type'] = str(type(charts))
        if isinstance(charts, dict) and 'songs' in charts:
             output['charts_sample'] = charts['songs']['items'][0] if charts['songs']['items'] else "Empty"
        else:
             output['charts_raw'] = str(charts)[:200]
    except Exception as e:
        print(f"get_charts failed: {e}")
        output['charts_error'] = str(e)

    try:
        print("\nTesting search fallback...")
        search_res = yt.search("trending", filter="songs", limit=5)
        print("search success!")
        output['search_type'] = str(type(search_res))
        if search_res:
            output['search_sample'] = search_res[0]
    except Exception as e:
        print(f"search failed: {e}")
        output['search_error'] = str(e)

    with open("reproduce_output.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    test_trending()
