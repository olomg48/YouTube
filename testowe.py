import pandas as pd
from matplotlib import pyplot as plt
data = pd.read_excel("siema.xlsx")
plt.style.use("ggplot")
data.set_index('Published', drop = True, inplace = True)
chart = data.plot.line(y = 'Views', use_index = True)
chart.set_ylim(100,25000000)

plt.show()