import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def main():
    api_service_name = "youtube"
    api_version = "v3"
    winner_info = "winner_info.txt"
    found = False

    # PUT YOUR API KEY HERE
    DEVELOPER_KEY = "YOUR API KEY"
    # SET THE SECRET PASSWORD OR PASSPHRASE HERE
    SECRET_PASSWORD = "PASSWORD"
    # PUT THE ID OF THE VIDEO HERE
    VID_ID = "VID ID"

    # Search through comments:
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    next_page_token = None

    # Kept for progress report only
    comment_processed = 0

    # Can only process 100 comments at a time, so do until no more comments exist:
    while True:
        comment_texts = []

        request = youtube.commentThreads().list(
            part="snippet",
            videoId=VID_ID,
            maxResults=100,
            pageToken=next_page_token
        )
        response = request.execute()

        # Add the text from every reply comment to the comment_texts list
        for item in response["items"]:
            comment_processed += 1
            text = "COMMENT:\t" + item['snippet']['topLevelComment']['snippet']['textDisplay'] + f"\t\tAUTHOR OF COMMENT: {item['snippet']['topLevelComment']['snippet']['authorDisplayName']}" + f"\nLINK TO COMMENT: https://www.youtube.com/watch?v={VID_ID}&lc={item['snippet']['topLevelComment']['id']}"
            
            if SECRET_PASSWORD.lower() in text.lower():
                found = True
                print(f"processed {comment_processed} comments")
                print("\nFOUND SECRET PASSWORD\n")
                with open("winner_info.txt", "w") as f:
                    f.write(text)
                make_private(VID_ID)
                break

        print(f"processed {comment_processed} comments")

        if found:
            break

        if not "nextPageToken" in response:
            break

        next_page_token = response["nextPageToken"]

    if not found:
        print("\nSecret password was not found.\n")


# Make the video private if the secret password is found
def make_private(id):
    scopes = ["https://www.googleapis.com/auth/youtube"]

    # Disable OAuthlib's HTTPS verification when running locally.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes
    )
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials
    )

    request = youtube.videos().update(
        part="status", body={"id": id, "status": {"privacyStatus": "private"}}
    )

    response = request.execute()

    print(response)


if __name__ == "__main__":
    main()
