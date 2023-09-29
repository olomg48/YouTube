Welcome to my repository!
This is my project about analyzing YouTube data with YouTubeAPI, Python, and PowerBI.
In "search_for_new_videos.py", you can find my solution to load data from YouTubeAPI into Azure Blob Storage. Then, my output CSV file is loaded with Azure Data Factory into an MS SQL Server database, and I can analyze this data with a Power BI dashboard. My dashboard can be accessed from this link: https://www.novypro.com/project/youtube-data-analysis

In my database, there is data about a few YouTube channels and all their videos. New videos are being added to the database every day at 9 PM. On my Power BI dashboard, you can track trends in views and video count, check viewers' engagement rate, or see the correlation between views and video duration for different video categories over different periods of time.

Key technologies:
 - YouTube API
 - Microsoft Power BI
 - DAX
 - Python (pandas)
 - Azure Blob Storage
 - Azure Data Factory
 - MS SQL Server


In "studies_project.py", there is a small python program, that collects data from YouTube API, and analyzes it with Python pandas and matplotlub. I also created some basic GUI with Tkinter. It provides only basic analysis, but this project allowed me to learn how to work with API and make basic visuals in Python
