# Standard library imports
import math
import random
import unittest
from datetime import datetime
from os import getenv
from typing import List, Tuple

# Third-party imports
from dotenv import load_dotenv
import pandas as pd
import psycopg2

# Constants
RANKS = ['Private', 'Lieutenant', 'Captain', 'Commander']
RANK_PROBABILITIES = [round(random.uniform(0.0, 0.2), 2),
                      round(random.uniform(0.2, 0.25), 2),
                      round(random.uniform(0.25, 0.3), 2),
                      round(random.uniform(0.3, 0.37), 2)]

CLONE_TYPES = ['Standard', 'Heavy', 'Commando', 'ARC Trooper']
CLONE_TYPE_PROBABILITIES = [round(random.uniform(0.0, 0.2), 2),
                            round(random.uniform(0.2, 0.25), 2),
                            round(random.uniform(0.25, 0.3), 2),
                            round(random.uniform(0.3, 0.37), 2)]

ASSIGNED_WEAPONS = ["DC-15A Blaster Rifle", "DC-15X Sniper Rifle", "DC-17m Blaster Rifle",
                    "DC-15S Blaster Carbine", "WESTAR-M5 Blaster Rifle"]

ASSIGNED_GENERALS = ['General Mace Windu', 'General Yoda', 'General Kenobi', 'General Skywalker']
ASSIGNED_GENERAL_PROBABILITIES = [round(random.uniform(0.0, 0.2), 2),
                                  round(random.uniform(0.2, 0.25), 2),
                                  round(random.uniform(0.25, 0.3), 2),
                                  round(random.uniform(0.3, 0.37), 2)]


class Database:
    """Database class for managing and manipulating clone trooper records."""
    load_dotenv()

    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            host=getenv("DB_HOST")
        )
        self.cur = self.conn.cursor()

    def create_table(self):
        """Create table in the database if it doesn't already exist."""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS clone_troopers (
                ct_id SERIAL PRIMARY KEY,
                clone_type VARCHAR(50),
                rank VARCHAR(50),
                assigned_weapon VARCHAR(50),
                health INTEGER,
                energy INTEGER,
                success_percentage NUMERIC,
                assigned_general VARCHAR(50),
                check_in_time TIMESTAMP
            )
        """)
        self.conn.commit()

    def seed(self, amount: int):
        """Insert generated data into the database."""
        data = self.generate_clone_trooper(amount)
        for row in data:
            self.cur.execute("""
                INSERT INTO clone_troopers (clone_type, rank, assigned_weapon, health, energy, success_percentage, assigned_general, check_in_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, row)
        self.conn.commit()

    def reset(self) -> int:
        """Delete all records from the table and return the number of deleted rows."""
        self.cur.execute("DELETE FROM clone_troopers")
        self.conn.commit()
        return self.cur.rowcount

    def count(self) -> int:
        """Count the number of records in the table."""
        self.cur.execute("SELECT COUNT(*) FROM clone_troopers")
        return self.cur.fetchone()[0]

    def dataframe(self) -> pd.DataFrame:
        """Retrieve table data as a pandas DataFrame."""
        self.cur.execute("SELECT * FROM clone_troopers")
        rows = self.cur.fetchall()
        columns = [desc[0] for desc in self.cur.description]
        return pd.DataFrame(rows, columns=columns)

    def html_table(self) -> str:
        """Generate HTML table from DataFrame data."""
        df = self.dataframe()
        return df.to_html()

    @staticmethod
    def generate_clone_trooper(n: int) -> List[Tuple]:
        """Generate data for 'n' clone troopers."""
        data = []
        for _ in range(n):
            clone_type_index = random.choices(range(len(CLONE_TYPES)), CLONE_TYPE_PROBABILITIES, k=1)[0]
            clone_type = CLONE_TYPES[clone_type_index]
            rank_index = random.choices(range(len(RANKS)), RANK_PROBABILITIES, k=1)[0]
            rank = RANKS[rank_index]
            assigned_weapon = random.choice(ASSIGNED_WEAPONS)
            health = random.randint(3, 9)
            energy = random.randint(2, 6)
            general_index = random.choices(range(len(ASSIGNED_GENERALS)), ASSIGNED_GENERAL_PROBABILITIES, k=1)[0]
            general = ASSIGNED_GENERALS[general_index]
            success_percentage = round(random.uniform(0.1, 0.3), 2)  # Example percentage calculation.
            check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data.append((clone_type, rank, assigned_weapon, health, energy, success_percentage, general, check_in_time))
        return data

class TestDatabase(unittest.TestCase):
    """Unit tests for the Database class."""

    def setUp(self):
        self.db = Database()

    def test_connection(self):
        self.assertIsNotNone(self.db.conn)

    def test_seed(self):
        self.db.reset()
        self.db.seed(10)
        self.assertEqual(self.db.count(), 10)

    def test_reset(self):
        self.db.reset()
        self.db.seed(10)
        self.db.reset()
        self.assertEqual(self.db.count(), 0)

    def test_count(self):
        self.db.reset()
        self.db.seed(5)
        self.assertEqual(self.db.count(), 5)

    def test_dataframe(self):
        self.db.reset()
        self.db.seed(5)
        df = self.db.dataframe()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)

    def test_html_table(self):
        self.db.reset()
        self.db.seed(5)
        html = self.db.html_table()
        self.assertIsInstance(html, str)
        self.assertTrue('<table' in html)

        self.db.reset()
        html = self.db.html_table()
        self.assertTrue('<tbody>\n  </tbody>' in html)  # Check if the table body is empty

if __name__ == '__main__':
    unittest.main()