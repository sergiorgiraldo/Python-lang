import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys
from typing import List, Dict
import time

class SpotifyPlaylistFinder:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        scope = "playlist-read-private playlist-read-collaborative"
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        ))
        
    def find_song_in_playlists(self, song_name: str, artist_name: str = None) -> List[Dict]:
        print(f"Searching for '{song_name}'" + (f" by {artist_name}" if artist_name else ""))
        print("-" * 50)
        
        playlists = self._get_all_user_playlists()
        
        found_in_playlists = []
        
        for playlist in playlists:
            playlist_name = playlist['name']
            playlist_id = playlist['id']
            
            # print(f"Searching in playlist: {playlist_name}")
            
            if self._is_song_in_playlist(playlist_id, song_name, artist_name):
                playlist_info = {
                    'name': playlist_name,
                    'id': playlist_id,
                    'url': playlist['external_urls']['spotify'],
                    'tracks_total': playlist['tracks']['total'],
                    'owner': playlist['owner']['display_name']
                }
                found_in_playlists.append(playlist_info)
            #     print(f"  ✓ Found in '{playlist_name}'")
            # else:
            #     print(f"  ✗ Not found in '{playlist_name}'")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return found_in_playlists
    
    def _get_all_user_playlists(self) -> List[Dict]:
        playlists = []
        results = self.sp.current_user_playlists(limit=50)
        
        while results:
            playlists.extend(results['items'])
            if results['next']:
                results = self.sp.next(results)
            else:
                break
                
        return playlists
    
    def _is_song_in_playlist(self, playlist_id: str, song_name: str, artist_name: str = None) -> bool:
        try:
            results = self.sp.playlist_tracks(playlist_id)
            tracks = results['items']
            
            while results['next']:
                results = self.sp.next(results)
                tracks.extend(results['items'])
            
            for item in tracks:
                if item['track'] is None:
                    continue
                    
                track = item['track']
                track_name = track['name'].lower()
                track_artists = [artist['name'].lower() for artist in track['artists']]
                
                if song_name.lower() in track_name or track_name in song_name.lower():
                    if artist_name:
                        if any(artist_name.lower() in artist for artist in track_artists):
                            return True
                    else:
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error searching playlist: {e}")
            return False

def main():
    # https://developer.spotify.com/dashboard
    CLIENT_ID = "81264177704045079e3e8c71e79d09b9"
    CLIENT_SECRET = "feb7a4d2c2b14e58a803ce64b9c2154d"
    REDIRECT_URI = "https://example.com/callback"  
    
    try:
        finder = SpotifyPlaylistFinder(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
        
        if len(sys.argv) > 1:
            song_name = " ".join(sys.argv[1:])
        else:
            song_name = input("Enter the song name: ").strip()
        
        if not song_name:
            print("Please provide a song name!")
            return
        
        artist_name = input("Enter artist name (optional, press Enter to skip): ").strip()
        artist_name = artist_name if artist_name else None
        
        found_playlists = finder.find_song_in_playlists(song_name, artist_name)
        
        print("\n" + "=" * 50)
        print("RESULTS")
        print("=" * 50)
        
        if found_playlists:
            print(f"Found '{song_name}' in {len(found_playlists)} playlist(s):\n")
            
            for i, playlist in enumerate(found_playlists, 1):
                print(f"{i}. {playlist['name']}")
                print(f"   Owner: {playlist['owner']}")
                print(f"   Total tracks: {playlist['tracks_total']}")
                print(f"   URL: {playlist['url']}")
                print()
        else:
            print(f"'{song_name}' was not found in any of your playlists.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure you have the 'spotipy' library installed: pip install spotipy")

if __name__ == "__main__":
    main()