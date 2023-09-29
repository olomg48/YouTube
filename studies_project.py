from googleapiclient.discovery import build
from matplotlib import pyplot
import pandas
import matplotlib.ticker as ticker
import tkinter as tk

# do odpalenia programu trzeba zainstalować:
# #google-auth-oauthlib #google-auth-httplib2 #matplotlib #pandas #google-api-python-client

#
api_key = ""
youtube = build('youtube', 'v3', developerKey = api_key)

szukany_kanal = input("Podaj kanal dla ktorego chcesz otrzymac statystyki: ")

channel_topics = []
topics_str = ""
comments = []
likes = []
dates = []
views = []
ids = []
duration = []
category = []
i = 0
nextpage = ""
q = False

window = tk.Tk()
window.geometry("800x800")


def playlista_kanalu(channel):
    response = youtube.search().list(q=channel, type='channel', part='id').execute()
    channel_id = response["items"][0]["id"]["channelId"]
    kanal = youtube.channels().list(
        part = 'contentDetails, topicDetails',
        id = channel_id
    ).execute()
    playlista = kanal["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    #tematy kanalu
    for topic in kanal["items"][0]["topicDetails"]["topicCategories"]:
        channel_topics.append(topic[30:])

    return (playlista)

def kategorie(id):
    match id:
        case 1: return "Film & Animation"
        case 2: return "Autos & Vehicles"
        case 10: return "Music"
        case 15: return "Pets & Animals"
        case 17: return "Sports"
        case 18: return "Short Movies"
        case 19: return "Travel & Events"
        case 20: return "Gaming"
        case 21: return "Videoblogging"
        case 22: return "People & Blogs"
        case 23: return "Comedy"
        case 24: return "Entertainment"
        case 25: return "News & Politics"
        case 26: return "Howto & Style"
        case 27: return "Education"
        case 28: return "Science & Technology"
        case 29: return "Nonprofits & Activism"
        case 30: return "Movies"
        case 31: return "Anime/Animation"
        case 32: return "Action/Adventure"
        case 33: return "Classics"
        case 34: return "Comedy"
        case 35: return "Documentary"
        case 36: return "Drama"
        case 37: return "Family"
        case 38: return "Foreign"
        case 39: return "Horror"
        case 40: return "Sci-Fi/Fantasy"
        case 41: return "Thirrler"
        case 42: return "Shorts"
        case 43: return "Shows"
        case 44: return "Trailers"


#szukanie playlisty dla kanalu

playlist_id = playlista_kanalu(szukany_kanal)


#przelatuje po calej playliscie kanalu
while (True):
    playlist_item = youtube.playlistItems().list(
    part = 'ContentDetails',
    playlistId = playlist_id,
    maxResults = 300,
    pageToken = nextpage
    ).execute()

    #przelatuje po danej stronie (50 elementow). Ogolnie kazdy item z playlist_item to jedno video, ale
    #z playlistItems() nie mozna wyciagnac statistics, dlatego trzeba robic osobnego requesta na kazde video
    for rep in playlist_item["items"]:
        i += 1
        video = youtube.videos().list(
            part = 'statistics, snippet, contentDetails',
            id = rep["contentDetails"]["videoId"],
        ).execute()
        #print(rep["contentDetails"]["videoId"])

        #transmisje live nie mają liczby wyświetleń
        try:
            views.append(int(video["items"][0]["statistics"]["viewCount"]))
            ids.append(rep["contentDetails"]["videoId"])
            dates.append(rep["contentDetails"]["videoPublishedAt"][:10])
            category_id = int(video["items"][0]["snippet"]["categoryId"])
            category.append(kategorie(category_id))
            likes.append(int(video["items"][0]["statistics"]["likeCount"]))
            dlugosc = video["items"][0]["contentDetails"]['duration']
            dlugosc = pandas.to_timedelta(dlugosc)
            dlugosc = dlugosc.seconds/60
            #print(dlugosc.seconds/60)
            duration.append(dlugosc)
                # niektóre filmy mają wyłączone komentarze
            try:
                comments.append(int(video["items"][0]["statistics"]["commentCount"]))
            except:
                comments.append(0)
        except:
            pass

        #wyskakiwanie z while, jesli nie ma ['nextPageToken'], to oznacza, ze jest to ostatnia strona
        #q=true oznacza ostatnia strone i koniec petli
        try:
            nextpage = playlist_item['nextPageToken']
        except:
            q = True
    if q: break

#ustawianie DataFrame'u z liczbami z pętli powyżej
dates = pandas.to_datetime(dates)
data = pandas.DataFrame()
data['ID'] = ids
data["Views"] = views
data['Published'] = dates
data["Category"] = category
data["Likes"] = likes
data["Comments"] = comments
data["Duration [m]"] = duration

#tworzy formatter, który ustawia format wykresu na taki z liczbami numerycznymi a nie w formacie naukowym
formatter = ticker.ScalarFormatter(useMathText=True)
formatter.set_scientific(False)

# ustawia format wypisywania liczb w pandas
pandas.set_option('display.float_format', '{:,.2f}'.format)

# grupuje żeby policzyć średnią dla każdej kategorii
avg_views = data.groupby("Category")["Views"].mean()
avg_likes = data.groupby("Category")["Likes"].mean()
avg_coms = data.groupby("Category")["Comments"].mean()

#lambda zwraca wszystkie x dla ktorych wartosc avg_views jest rowna max
#index[0], poniewaz ponizszy wiersz zwraca index jako obiekt, ktory zawier rowniez inne atrybuty niz nazwa
top_cat_views = avg_views.loc[lambda x: x == avg_views.max()].index[0]
top_cat_likes = avg_likes.loc[lambda x: x == avg_likes.max()].index[0]
top_cat_coms = avg_coms.loc[lambda x: x == avg_coms.max()].index[0]

#grupowanie i zliczanie ID per kategoria
cat_count = data.groupby("Category")["ID"].count()

#usuniecie naglowka i informacji o typie danych poprzez transformacje Series na string
cat_count = cat_count.to_string(header = False)

#oblicza ogólną średnią wyświetleń dla kanału
avg_views_all = int(data["Views"].mean())
avg_likes_all = int(data["Likes"].mean())
avg_coms_all = int(data["Comments"].mean())

#funkcja do rysowania wykresu ze średnią wyświetleń/lajków/komentarzy per kategoria
def average_plot(column, color):

        if(column == "Likes"):
            avg = avg_likes
            top_cat = top_cat_likes
        elif(column=="Comments"):
            avg = avg_coms
            top_cat = top_cat_coms
        else:
            avg = avg_views
            top_cat = top_cat_views

        # ustawianie wielkości okna w którym jest wykres
        pyplot.figure(figsize=(12, 14))

        # tworzy wykres, bar chart, nadaje tytuł i osie
        avg_plot = avg.plot(kind="bar", title=f"Average {column} number by category for {szukany_kanal}",
                                        x="Category", y=f"{column}", color = color)

        # ustawia formatter dla osi y, żeby liczby były pokazywane numerycznie a nie naukowo
        avg_plot.yaxis.set_major_formatter(formatter)

        # tworzy labele dla kolumn, ustawia format
        # containers to grupa słupków na wykresie, czyli containers[0] to pierwsza grupa słupków
        avg_plot.bar_label(avg_plot.containers[0], label_type='edge', fmt='{:,.0f}')

        # ustawia pochylenie dla podpisów pod kategoriami
        # ticks to punkty na osi
        avg_plot.set_xticklabels(avg_plot.get_xticklabels(), rotation=20)

        #włączanie legendy na wykresie
        pyplot.legend()
        #pokazanie wykresu
        pyplot.show()


#funkcja do rysowania wykresu przedstawiającego liczbę wyświetleń/lajków/komentarzy w czasie
def time_plot(column, color):

    # utworzenie wykresu pokazującego wyświetlenia w czasie
    time_data = data.plot(kind="line", title=f"{column} number by time for {szukany_kanal}", x="Published", y=f"{column}", color = color)

    # ustawienie formattera dla drugiego wykresu
    time_data.yaxis.set_major_formatter(formatter)
    # włączanie legendy na wykresie
    pyplot.legend()
    # pokazanie wykresu
    pyplot.show()



# funkcje do wyświetlania wykresów uruchamiane przez tkintera
def average_likes_plot():
    average_plot("Likes", "hotpink")

def average_views_plot():
    average_plot("Views", "turquoise")

def average_coms_plot():
    average_plot("Comments", "lime")

def time_views_plot():
    time_plot("Views", "turquoise")

def time_coms_plot():
    time_plot("Comments", "lime")

def time_likes_plot():
    time_plot("Likes", "hotpink")


#LABELE
tytul = tk.Label(window, text = f"Analiza dla kanalu {szukany_kanal}", font = ("Arial", 25))
tytul.pack()

for topic_str in channel_topics:
    topics_str += topic_str + ", "
label8 = tk.Label(window, text=f"Tematy kanalu: {topics_str[:-2]}", font = ("Arial", 15))
label8.pack()

label2 = tk.Label(window, text=f"Liczba filmow z podzialem na kategorie: \n {cat_count}", pady=5, font=("Arial", 13))
label2.pack()

label11 = tk.Label(window, text=f"Sredni czas trwania filmu: {round(data['Duration [m]'].mean(),2)}min.", font=("Arial", 13))
label11.pack()

tk_views = tk.LabelFrame(window, text="Analiza liczby wyswietlen", width=500, height=150)
#wyłącza dostosowanie rozmiaru LabelFrame do rozmiarów labeli i buttonów wewnątrz niej
tk_views.pack_propagate(False)
tk_views.pack(pady = 15)

tk_coms = tk.LabelFrame(window, text="Analiza liczby komentarzy",width=500, height=170)
tk_coms.pack_propagate(False)
tk_coms.pack(pady = 15)

tk_likes = tk.LabelFrame(window, text="Analiza liczby lajkow",width=500, height=170)
tk_likes.pack_propagate(False)
tk_likes.pack(pady = 15)

label1 = tk.Label(tk_views, text=f"Najwieksza srednia liczba wyswietlen na film: {top_cat_views}", pady=2)
label1.pack()

label3 = tk.Label(tk_views, text = f"Srednia wyswietlen dla wszystkich filmow: {avg_views_all}", pady=2)
label3.pack()

label9 = tk.Label(tk_coms, text=f"Najwieksza srednia liczba komentarzy na film: {top_cat_coms}", pady=2)
label9.pack()

label10 = tk.Label(tk_likes, text=f"Najwieksza srednia liczba lajkow na film: {top_cat_likes}", pady=2)
label10.pack()

label4 = tk.Label(tk_likes, text = f"Srednia lajkow dla wszystkich filmow: {avg_likes_all}", pady=2)
label4.pack()

label7 = tk.Label(tk_likes, text=f"Srednia liczba lajkow na wyswietlenie: {round(avg_likes_all/avg_views_all,3)}", pady=2)
label7.pack()


label5 = tk.Label(tk_coms, text = f"Srednia komentarzy dla wszystkich filmow: {avg_coms_all}", pady=2)
label5.pack()

label6 = tk.Label(tk_coms, text=f"Srednia liczba komentarzy na wyswietlenie: {round(avg_coms_all/avg_views_all,3)}", pady=2)
label6.pack()



# PRZYCISKI

average_views_btn = tk.Button(tk_views, text = "Srednia liczba wyswietlen na kategorie", command=average_views_plot, pady=5)
average_views_btn.pack()

time_views_btn = tk.Button(tk_views, text="Liczba wyswietlen w czasie", command=time_views_plot, pady=5)
time_views_btn.pack()

average_likes_btn = tk.Button(tk_likes, text = "Srednia liczba lajkow na kategorie", command=average_likes_plot, pady=5)
average_likes_btn.pack()

time_likes_btn = tk.Button(tk_likes, text="Liczba lajkow w czasie", command=time_likes_plot, pady=5)
time_likes_btn.pack()

average_coms_btn = tk.Button(tk_coms, text = "Srednia liczba komentarzy na kategorie", command=average_coms_plot, pady=5)
average_coms_btn.pack()

time_coms_btn = tk.Button(tk_coms, text="Liczba komenatarzy w czasie", command=time_coms_plot, pady=5)
time_coms_btn.pack()

print(data)
window.mainloop()

#zapisanie do excela do dalszej analizy
data.to_excel("dane_z_youtube.xlsx")

