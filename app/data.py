from os import getenv
import random
from datetime import datetime
import math
from certifi import where
from dotenv import load_dotenv
from MonsterLab import Monster
from pandas import DataFrame
from pymongo import MongoClient
from typing import Dict, Iterable, Iterator

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

asssigned_weapons = ["DC-15A Blaster Rifle",
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
    def __init__(self, collection: str):
        self.db = MongoDB(collection)

    def seed(self, amount):
        data = self.generate_clone_trooper(amount)
        self.db.create_many(data)

    def reset(self):
        self.db.delete_all()

    def count(self) -> int:
        return self.db.count_documents()

    def dataframe(self) -> DataFrame:
        return self.db.to_dataframe()

    def html_table(self) -> str:
        return self.db.to_html_table()

    @staticmethod
    def generate_clone_trooper(n):
        data = []
        for _ in range(n):
            clone_trooper_name = f"CT-{random.randint(0, 999999):06}"
            # ... rest of your code here ...
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


class MongoDB:
    load_dotenv()
    database = MongoClient(getenv("DB_URL") + "&tls=true&tlsInsecure=true")["Database"]
    # load_dotenv()
    # database = MongoClient(getenv("DB_URL"), tlsCAFile=where())["Database"]

    def __init__(self, collection: str):
        self.collection = self.database[collection]

    def create_one(self, record: Dict) -> bool:
        return self.collection.insert_one(record).acknowledged

    def read_one(self, query: Dict) -> Dict:
        return self.collection.find_one(query, {"_id": False})

    def update_one(self, query: Dict, update: Dict) -> bool:
        return self.collection.update_one(query, {"$set": update}).acknowledged

    def delete_one(self, query: Dict) -> bool:
        return self.collection.delete_one(query).acknowledged

    def create_many(self, records: Iterable[Dict]) -> bool:
        return self.collection.insert_many(records).acknowledged

    def read_many(self, query: Dict) -> Iterator[Dict]:
        return self.collection.find(query, {"_id": False})

    def update_many(self, query: Dict, update: Dict) -> bool:
        return self.collection.update_many(query, {"$set": update}).acknowledged

    def delete_many(self, query: Dict) -> bool:
        return self.collection.delete_many(query).acknowledged

    def reset(self):
        self.db.delete_all()

    def count(self) -> int:
        return self.db.count_documents()

    def dataframe(self) -> DataFrame:
        return self.db.to_dataframe()

    def html_table(self) -> str:
        return self.db.to_html_table()
    
    def count_documents(self) -> int:
        return self.collection.count_documents({})

# if __name__ == '__main__':
#     db = MongoDB("Collection")
#     db.create_many({"Value": randrange(1, 100)} for _ in range(10))
#     print(DataFrame(db.read_many({})))

# import unittest
# from data import Database

# class TestDatabase(unittest.TestCase):
#     def setUp(self):
#         self.db = Database('test_collection')

#     def test_seed(self):
#         self.db.seed(10)
#         self.assertEqual(self.db.count(), 10)

#     def test_reset(self):
#         self.db.reset()
#         self.assertEqual(self.db.count(), 0)

#     def test_dataframe(self):
#         self.db.seed(10)
#         df = self.db.dataframe()
#         self.assertEqual(len(df), 10)

#     def test_html_table(self):
#         self.db.seed(10)
#         html = self.db.html_table()
#         self.assertIsNotNone(html)

# if __name__ == '__main__':
#     unittest.main()