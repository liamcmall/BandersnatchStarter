# Imports
import pandas as pd
import math
import random
from datetime import datetime
import plotly.express as px
from app.data2 import Database  # Import the Database class

db = Database()
df = db.dataframe()

def chart(df, x, y, target):
    fig = px.box(df, x=x, y=y, title=target)
    fig.show()
