import threading
from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import PyMongoError
import json


class ProductCache:
    def __init__(self, mongo_uri: str, db_name: str, collection_name: str):
        self.client = MongoClient(mongo_uri)
        self.collection = self.client[db_name][collection_name]

        # Internal dictionary storage for the full collection
        self._cache = {}
        # Thread lock to prevent issues if multiple threads reload data simultaneously
        self._lock = threading.Lock()

        # Initial load of all records at startup
        self.reload_all_products()

    def reload_all_products(self):
        """Fetches the entire collection from MongoDB and replaces the cache."""
        with self._lock:
            print("🔄 Loading/Refreshing complete product catalog into memory...")
            new_cache = {}

            try:
                # self.loadMongoData()
                self.loadData()
                print(f"Cache ready. {len(self._cache)} products loaded.")

            except PyMongoError as e:
                print(f"Mongo failed ..")
                self.loadData()

    def get_product(self, product_id: str) -> dict:
        return self._cache.get(product_id)

    def get_all_products(self) -> list:
        """Instantly returns the full list of products from RAM."""
        return list(self._cache.values())

    def loadData(self):
        print(f"load mock data...")
        mock_data = [
            {
                "_id": "6a762ba92d996dcaab93c69e",
                "item": "testAddProduct1",
                "category": "Cosmetics",
                "price": 50,
                "brand": "tusker",
                "model": "Elite Premium",
                "date": "2026-08-07T19:02:01.799000",
            },
            {
                "_id": "6a762ba92d996dcaab93c69e1",
                "item": "testAddProduct1",
                "category": "Cosmetics",
                "price": 50,
                "brand": "tusker",
                "model": "Elite Premium",
                "date": "2026-08-07T19:02:01.799000",
            },
        ]

        new_cache = {}

        try:
            with open("collection_db.txt", "r", encoding="utf-8") as file:
                products = json.load(file)
        except FileNotFoundError:
            products = mock_data

        for product in products:
            p_id = str(product["_id"])
            product["_id"] = p_id
            product["image_url"] = (
                "https://res.cloudinary.com/hvuzvzcp/image/upload/v1786250019/cld-sample-4.jpg"
            )
            new_cache[p_id] = product

        self._cache = new_cache
        print(f"Cache ready. {len(self._cache)} products loaded.")

    def loadMongoData(self):
        print(f"load data from Mongodb...")
        cursor = self.collection.find({})
        new_cache = {}
        for product in cursor:
            p_id = str(product["_id"])
            product["_id"] = p_id
            new_cache[p_id] = product

        # Atomic swap of the old cache dictionary with the new one
        self._cache = new_cache
