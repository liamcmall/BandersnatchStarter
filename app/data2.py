# Standard library imports
from datetime import datetime
from os import getenv
import math
import random
import unittest

from dotenv import load_dotenv
import pandas as pd

import psycopg2

# Typing
from typing import Dict, Iterable, Iterator, List, Tuple

# List and Etc.

ranks = ['Private', 'Sergeant', 'Lieutenant', 'Captain', 'Commander']
rank_probabilities = [round(random.uniform(0.0,0.1),2),
                      round(random.uniform(0.1,0.15),2),
                      round(random.uniform(0.2,0.25),2),
                      round(random.uniform(0.25,0.3),2),
                      round(random.uniform(0.3,0.35),2)]

clone_types = ['Standard','Recon', 'Heavy', 'Commando', 'ARC Trooper']
clone_type_probabilities = [round(random.uniform(0.0,0.1),2),
                            round(random.uniform(0.1,0.15),2),
                            round(random.uniform(0.2,0.25),2),
                            round(random.uniform(0.25,0.3),2),
                            round(random.uniform(0.3,0.35),2)]

assigned_weapons = ["DC-15A Blaster Rifle",
                   "DC-15X Sniper Rifle",
                   "DC-17m Blaster Rifle",
                   "DC-15S Blaster Carbine",
                   "WESTAR-M5 Blaster Rifle"]

assigned_generals = ['General Mace Windu', "General Plo Koon", 'General Yoda', 'General Kenobi', 'General Skywalker',]
assigned_general_probabilities = [round(random.uniform(0.0,0.1),2),
                                  round(random.uniform(0.1,0.15),2),
                                  round(random.uniform(0.2,0.25),2),
                                  round(random.uniform(0.25,0.3),2),
                                  round(random.uniform(0.3,0.35),2)]


class Database:
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

    def seed(self, amount):
        data = self.generate_clone_trooper(amount)
        for row in data:
            self.cur.execute("""
                INSERT INTO clone_troopers (clone_type, rank, assigned_weapon, health, energy, success_percentage, assigned_general, check_in_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, row)
        self.conn.commit()
    
    def reset(self) -> int:
        self.cur.execute("DELETE FROM clone_troopers")
        self.conn.commit()
        return self.cur.rowcount

    def count(self) -> int:
        self.cur.execute("SELECT COUNT(*) FROM clone_troopers")
        return self.cur.fetchone()[0]

    def dataframe(self) -> pd.DataFrame:
        self.cur.execute("SELECT * FROM clone_troopers")
        rows = self.cur.fetchall()
        columns = [desc[0] for desc in self.cur.description]
        return pd.DataFrame(rows, columns=columns)

    def html_table(self) -> str:
        df = self.to_dataframe()
        return df.to_html()

    # Generate a random clone trooper!
    @staticmethod
    def generate_clone_trooper(n: int) -> List[Tuple]:
        data = []
        for _ in range(n):
            clone_type = random.choices(clone_types, clone_type_probabilities)[0]
            rank = random.choices(ranks, rank_probabilities)[0]
            assigned_weapon = random.choice(assigned_weapons)
            health = random.randint(3, 9)
            energy = random.randint(2, 6)
            assigned_general = random.choices(assigned_generals, assigned_general_probabilities)[0]
            success_percentage = round(sum([random.uniform(0, 0.35), math.log10(health)-0.80]), 2)
            check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data.append((clone_type, rank, assigned_weapon, health, energy, success_percentage, assigned_general, check_in_time))
        return data
    
class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()  # Adjust this to match your setup

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
        self.assertIsInstance(df, DataFrame)
        self.assertEqual(len(df), 5)

    def test_html_table(self):
        self.db.reset()
        self.db.seed(5)
        html = self.db.html_table()
        self.assertIsInstance(html, str)
        self.assertTrue('<table' in html)

        self.db.reset()
        html = self.db.html_table()
        self.assertIsNone(html)

if __name__ == '__main__':
    unittest.main()



