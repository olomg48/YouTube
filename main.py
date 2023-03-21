import json
from googleapiclient.discovery import build
import pprint
from matplotlib import pyplot
import openpyxl
import pandas
#id gimpera: UCFBH3Bdhgh3_cCToEQsUp6Q
#playlista uploads gimpera: UUFBH3Bdhgh3_cCToEQsUp6Q

api_key = "AIzaSyDFF8CtQO7u-yHhCU4ccDW92qELwzzngpo"
youtube = build('youtube', 'v3', developerKey = api_key)

dates = []
views = []
ids = []
i = 0
nextpage = ""

while (True):
    request = youtube.playlistItems().list(
    part = 'ContentDetails',
    playlistId = 'UUFBH3Bdhgh3_cCToEQsUp6Q',
    maxResults = 300,
    pageToken = nextpage
    )
    playlist_item = request.execute()
    for rep in playlist_item["items"]:
        i += 1
        dates.append(rep["contentDetails"]["videoPublishedAt"][:10])
        video_request = youtube.videos().list(
            part = 'statistics',
            id = rep["contentDetails"]["videoId"],
        )
        try:
            video = video_request.execute()
        except: break
        views.append(int(video["items"][0]["statistics"]["viewCount"]))
        ids.append(rep["contentDetails"]["videoId"])
        try:
            nextpage = playlist_item['nextPageToken']
        except: break

dates = pandas.to_datetime(dates)
data = pandas.DataFrame()
data["Views"] = views
data['Published'] = dates
data['ID'] = ids
data.set_index('Published', inplace=True, drop=True)
data.plot()
print(data)
pyplot.show()
data.to_excel("siema.xlsx")

