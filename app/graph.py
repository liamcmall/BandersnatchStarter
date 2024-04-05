# Standard library imports
import math
import random
import unittest
from datetime import datetime

# Third-party imports
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Local application imports
from app.data2 import Database

# Create database instance and dataframe
db = Database()
df = db.dataframe()

def chart(df, x, y, target):
    """Generate a box plot for the given dataframe and axes."""
    fig = px.box(df, x=x, y=y, title=target)
    fig.update_layout(template='plotly_dark', autosize=True)
    return fig

class TestChart(unittest.TestCase):
    """Unit tests for the chart function."""
    
    def test_chart(self):
        """Test the chart function with a predefined DataFrame."""
        # Creates a random DataFrame
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