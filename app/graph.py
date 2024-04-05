# Imports
import pandas as pd
import math
import random
from datetime import datetime
import plotly.express as px
from app.data2 import Database
import plotly.io as pio
import unittest

db = Database()
df = db.dataframe()

def chart(df, x, y, target):
    fig = px.box(df, x=x, y=y, title=target)
    return fig


class TestChart(unittest.TestCase):
    def test_chart(self):
        # Creates a rando Dataframe
        df = pd.DataFrame({
            'clone_type': ['A', 'B', 'C'],
            'rank': [1, 2, 3],
            'health': [100, 200, 300],
            'assigned_general': ['X', 'Y', 'Z'],
            'success_percentage': [0.5, 0.6, 0.7]
        })

        fig = chart(df, 'rank', 'health', 'Test')

        self.assertEqual(type(fig).__name__, 'Figure')

if __name__ == '__main__':
    unittest.main()
