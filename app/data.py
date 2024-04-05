# Standard library imports
from datetime import datetime
from os import getenv
import math
import random
import unittest

# Misc  imports
from certifi import where
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import pandas as pd

# Typing
from typing import Dict, Iterable, Iterator


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

assigned_general = ['General Mace Windu', "General Plo Koon", 'General Yoda', 'General Kenobi', 'General Skywalker',]
assigned_general_probabilities = [round(random.uniform(0.0,0.1),2),
                                  round(random.uniform(0.1,0.15),2),
                                  round(random.uniform(0.2,0.25),2),
                                  round(random.uniform(0.25,0.3),2),
                                  round(random.uniform(0.3,0.35),2)]


class Database:
    load_dotenv()

    def __init__(self, collection_name: str):
        db_url = getenv("DB_URL")
        self.client = MongoClient(db_url,
                                  tlsCAFile=where(),
                                  tls=True,
                                  tlsAllowInvalidCertificates=True)["MainDatabase"]
        self.collection = self.client[collection_name]

    def seed(self, amount):
        data = self.generate_clone_trooper(amount)
        self.collection.insert_many(data)
    
    def reset(self) -> int:
        return self.collection.delete_many({}).deleted_count

    def count(self) -> int:
        return self.collection.count_documents({})

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(list(self.collection.find()))

    def to_html_table(self) -> str:
        df = self.to_dataframe()
        return df.to_html()

    # Generate a random clone trooper!
    @staticmethod
    def generate_clone_trooper(n):
        data = []
        for _ in range(n):

            # Select a clone type and its probability
            clone_type_index = random.choices(range(len(clone_types)), clone_type_probabilities, k=1)[0]
            clone_type = clone_types[clone_type_index]
            clone_type_probability = clone_type_probabilities[clone_type_index]

            # Select a rank and its probability
            rank_index = random.choices(range(len(ranks)), rank_probabilities, k=1)[0]
            rank = ranks[rank_index]
            rank_probability = rank_probabilities[rank_index]

            # Weapon Selected
            assigned_weapon = random.choice(assigned_weapons)

            # Random health and energy
            health = random.randint(3, 9)
            energy = random.randint(2, 6)

            # Select a general and its probability
            general_index = random.choices(range(len(assigned_general)), assigned_general_probabilities, k=1)[0]
            general = assigned_general[general_index]
            general_probability = assigned_general_probabilities[general_index]

            # Calculated the success percentage. But also included a skew towards healthier clones.
            success_percentage = round(sum([clone_type_probability, rank_probability, general_probability,math.log10(health)-0.80]), 2)

            data.append({
                "CT ID": clone_trooper_name,
                'Clone Type': clone_type,
                'Rank': rank,
                'Assigned Weapon': assigned_weapon,
                'Health': health,
                'Energy': energy,
                'Success Percentage': success_percentage,
                'Assigned General': general,
                'Check In Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        return data


## TESTING CENTER ###

class TestMongoDBConnection(unittest.TestCase):

    def setUp(self):
        db_url = getenv("DB_URL")
        # Set serverSelectionTimeoutMS to 5000 milliseconds (5 second)
        self.client = MongoClient(db_url,
                                  tlsCAFile=where(),
                                  tls=True,
                                  tlsAllowInvalidCertificates=True,
                                  serverSelectionTimeoutMS=5000)
        self.db_class = Database("test_collection")


    def test_connection(self):
        try:
            self.client.admin.command('ismaster')
        except ServerSelectionTimeoutError:
            self.fail("MongoDB connection failed.")

    def test_generate_clone_trooper(self):
        n = 5
        result = self.db_class.generate_clone_trooper(n)
        self.assertEqual(len(result), n)



if __name__ == '__main__':
    unittest.main()