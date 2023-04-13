My program allows to analyze YouTube channels data by category and number of views/likes/comments It requires API key for YouTube Data API.
You can analyze data for any YouTube channel. Program searches for name of the channel and shows you statistics
This video show how you can get your API key: https://youtu.be/th5_9woFJmk?t=34.
I used pandas dataframe to store formatted data, and matplotlib to visualize data from pandas DataFrames. I alsob built GUI with tkinter wich allowes to
show matplotlib charts.
Program counts some most important statistical measures, like sum or mean, for likes, comments, views and duration of video.

Tkinter interface for examplary channel:
![image](https://user-images.githubusercontent.com/60153574/231794408-7b89810f-871c-4015-a9ac-1ef1ae1101e2.png)

Buttons can show charts like this:
![image](https://user-images.githubusercontent.com/60153574/231794785-2ddf1175-2c97-4763-9f00-bc0439aef677.png)

Or this:
![image](https://user-images.githubusercontent.com/60153574/231794881-df88c28a-c90d-4241-a4ef-234ef88e0da1.png)

You have to install few python modules:
google-auth-oauthlib 
google-auth-httplib2 
matplotlib 
pandas 
google-api-python-client
