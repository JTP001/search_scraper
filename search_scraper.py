from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os
import json

file = open("api_key.json")
api_key = json.load(file)['api_key']
file.close
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def main():
    print("Enter a search bar query:")
    query = input()

    while True:
        print("Enter your desired video type to search for (any, video, stream):")
        video_type = input()
        if video_type == "any" or "video" or "stream":
            break
        print("Invalid value for video type")

    length = ""
    if (video_type == "stream"):
        length = "long"
    else:
        while True:
            print("Enter your desired video length to search for (any, long, medium, short):")
            length = input()
            if length == "any" or "long" or "medium" or "short":
                break
            print("Invalid value for length")
            
    print("Enter the title of your new playlist:")
    playlist_title = input()
    


    credentials = None

    if os.path.exists("token.json"):
        try:
            credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
        except (ValueError, KeyError):
            print("Invalid token.json file. It might be expired or corrupted.")

    if not credentials:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=8000)

        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    youtube = build(
        'youtube', 
        'v3', 
        developerKey=api_key,
        credentials=credentials
    )

    searchbar_request = youtube.search().list(
        part = 'id, snippet',
        q = query,
        maxResults = 25,
        type = 'video',
        videoDuration = length
    )

    searchbar_response = searchbar_request.execute()
    # Uncomment for full response report
    # print(searchbar_response)


    search_results = searchbar_response['items']

    # Creates an empty playlist
    playlist_request = youtube.playlists().insert(
        part = 'snippet, status',
        body = {
            "snippet": {
                "title": playlist_title,
                "description": "",
                "defaultLanguage": "en",
            },
            "status": {
                "privacyStatus": "private",
            }
        }
    )

    playlist_response = playlist_request.execute()
    # Uncomment for full response report
    # print(playlist_response)

    playlist_id = playlist_response['id']

    video_ids = []

    for video in search_results:
        video_id = video['id']['videoId']
        video_ids.append(video_id)

    if video_type == "any":
        playlist_videos = video_ids
    else:
        playlist_videos = []

        video_request = youtube.videos().list(
            fields = 'items(id, liveStreamingDetails)',
            part = 'id, liveStreamingDetails',
            maxResults = len(video_ids),
            id = ','.join(video_ids),
        )

        video_response = video_request.execute()
        # Uncomment for full response report
        # print(video_response)

        for video in video_response['items']:
            if video_type == "stream" and len(video) > 1:
                playlist_videos.append(video['id'])
            if video_type == "video" and len(video) == 1:
                playlist_videos.append(video['id'])
                

    # Populates the playlist with videos whose titles contain keyword, with a max of 50 videos.
    count = 0
    for video_id in playlist_videos:
        if count < 50:
            populate_request = youtube.playlistItems().insert(
                    part = 'snippet',
                    body = {
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {"kind": "youtube#video", "videoId": video_id},
                        },
                    }
                )
            populate_response = populate_request.execute()
            # Uncomment for full response report
            # print(populate_response)
            count += 1
    if count == 50:
        print("Limit of 50 videos reached. This limit can be changed inside the script.")




    


if __name__ == '__main__':
    main()