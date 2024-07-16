import subprocess
import json
import re

def get_playlist_info(playlist_url):
    try:
        # Run the SpotDL command to list tracks in the playlist
        result = subprocess.run(
            ['spotdl', 'url', playlist_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if the process was successful
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return []

        # Parse output
        track_details = []
        lines = result.stdout.splitlines()
        track_pattern = re.compile(r"^(\d+)\.\s+(.+?)\s+by\s+(.+?)\s+\[(.+?)\]$")

        for line in lines:
            match = track_pattern.match(line)
            if match:
                track_info = {
                    'track_number': int(match.group(1)),
                    'name': match.group(2),
                    'artist': match.group(3),
                    'duration': match.group(4)
                }
                track_details.append(track_info)

        return track_details
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return []

# Example usage
playlist_url = 'https://open.spotify.com/playlist/37i9dQZF1DWXRqgorJj26U'
track_details = get_playlist_info(playlist_url)

# Print track details in JSON format for readability
print(json.dumps(track_details, indent=4))
