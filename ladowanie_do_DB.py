import pandas as pd
from matplotlib import pyplot as plt
from mysql import connector

config = {
    'user': 'ogasior',
    'password': 'K2rTcuWFqoAW34CZ',
    'host': 'mysql.agh.edu.pl',
    'database': 'ogasior',
    'raise_on_warnings': True,
}

# nawiązanie połączenia
cnx = connector.connect(**config, autocommit = True)
cursor = cnx.cursor()

#wczytanie pliku do DataFrame
data = pd.read_excel("siema2.xlsx")
data.set_index('ID', drop = True, inplace = True)

#iteroewanie po dataframe
for index, row in data.iterrows():
    views = row["Views"]
    published = row["Published"].date()
    print(f"{index}, \t, {published}, \t, {views}")
    query = f'INSERT INTO Gimper VALUES ("{index}", "{published}", {views});'
    cursor.execute(query)





#wykres
#plt.style.use("ggplot")
#chart = data.plot.line(y = 'Views', use_index = True)
#chart.set_ylim(100,25000000)
#plt.show()

