import numpy
import pandas as pd
from pandas import *
from pandas import read_sql

con1 = DBConnection()

df1 = read_sql("SELECT * FROM table1", con1)
df2 = pd.read_sql(sql="SELECT * FROM table2", con=con1)

df3 = df1.join(df2, how="inner")
df4 = df1.set_index("key").join(df2.set_index("key"))
