import threading
from pymongo import MongoClient
from bson import ObjectId

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
            
            # Pull all 2,000 products in a single database query
            cursor = self.collection.find({})
            for product in cursor:
                # Convert ObjectId to string for easier frontend/API JSON use
                p_id = str(product["_id"])
                product["_id"] = p_id
                new_cache[p_id] = product
            
            # Atomic swap of the old cache dictionary with the new one
            self._cache = new_cache
            print(f"Cache ready. {len(self._cache)} products loaded.")

    def get_product(self, product_id: str) -> dict:
        """Instantly fetches a single product from RAM (No DB call)."""
        return self._cache.get(product_id)

    def get_all_products(self) -> list:
        """Instantly returns the full list of products from RAM."""
        return list(self._cache.values())
