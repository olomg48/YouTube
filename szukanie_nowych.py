import csv
from azure.storage.blob import BlobServiceClient
from googleapiclient.discovery import build
import pandas
from datetime import datetime
from datetime import timedelta
import os

# YouTube API setup
api_key = os.environ.get("YouTubeApi")
youtube = build('youtube', 'v3', developerKey = api_key)


# BLOB connection and files' names setup
connection_string = f"DefaultEndpointsProtocol=https;AccountName=storageaccountolomg;AccountKey={os.environ.get('BlobAccountKey')};EndpointSuffix=core.windows.net"
container_name = "kontener"
download_blob_name = "channels_playlists.csv"
upload_blob_name = "new.csv"
upload_file_path = "./new.csv"
download_file_path = "channels.csv"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)


# CSV output setup
output_file = open(upload_file_path, "w", newline ="")
writer = csv.writer(output_file, delimiter =";")
writer.writerow(["ID", "Views", "Likes", "Comments", "Duration", "CategoryID", "ChannelID", "Published"])

# necessary variables
last_page = False
video_query = ""
next_page = ""


# loading list with channels' playlists' ids
def download_blob():
    if os.path.exists(download_file_path):
        os.remove(download_file_path)

    with open(download_file_path, "wb") as f:
        f.write(blob_service_client.get_blob_client(container=container_name, blob=download_blob_name).download_blob().readall())
    with open(download_file_path, 'r') as f:
        id_list = list(csv.reader(f, delimiter=';'))[1:]
    return id_list


# YouTubeAPI request to get videos from channels' playlist
def get_channels_playlist(playlistID):
    playlist_items = youtube.playlistItems().list(
        part='ContentDetails',
        playlistId=playlistID,
        maxResults=300,
        pageToken=next_page
    ).execute()
    return playlist_items


# YouTubeAPI request to get data about exact video (likes, views, comments count etc.)
def get_video_data(videoID):
    video = youtube.videos().list(
        part='statistics, snippet, contentDetails',
        id=videoID,
    ).execute()["items"][0]
    return video


ids = download_blob()

for channel_playlistID in ids:
    last_page = False
    next_page = ""

    # lookup each channel's playlist searching for last day videos
    while (True):
        playlist_items = get_channels_playlist(playlistID=channel_playlistID[0])

        if(playlist_items["items"]==[]):
            break

        for rep in playlist_items["items"]:
            video = get_video_data(rep["contentDetails"]["videoId"])

            # live streams have no views count, and we don't want to load them
            try:
                views_count = int(video["statistics"]["viewCount"])
                video_id = rep["contentDetails"]["videoId"]
                video_published = pandas.to_datetime(rep["contentDetails"]["videoPublishedAt"][:10])

                if video_published >= pandas.to_datetime(datetime.today() - timedelta(days=3)):
                    category_id = video["snippet"]["categoryId"]
                    likes_count = int(video["statistics"]["likeCount"])
                    video_duration = pandas.to_timedelta(video["contentDetails"]['duration'])
                    video_duration = round(video_duration.seconds / 60, 2)

                    # some videos have disabled comments
                    try:
                        comments_count = int(video["statistics"]["commentCount"])
                        writer.writerow([video_id, views_count, likes_count, comments_count, video_duration, category_id, channel_playlistID[0], video_published])
                    except:
                        writer.writerow([video_id, views_count, likes_count, 0, video_duration, category_id, channel_playlistID[0], video_published])
                else:
                    # we want to search only videos from last day to load database, so we are ending loops
                    last_page = True
                    break
            except:
                pass

            # when ['nextPageToken'] is None, it means, that we've reached last page of playlist,
            # and we want to end our loop
            try:
                next_page = playlist_items['nextPageToken']
            except:
                last_page = True
        if last_page: break

output_file.close()

# sending csv file with new videos to Azure Blob Storage (overwrite if necessary)
with open(upload_file_path, "rb") as f:
    blob_service_client.get_blob_client(container=container_name, blob=upload_blob_name).upload_blob(f, overwrite = True)

