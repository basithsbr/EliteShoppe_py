from contextlib import asynccontextmanager
from itertools import product
from elite_shoppe_app.ProductCache import ProductCache
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from functools import cache
import time

# Replace this with your actual local or MongoDB Atlas connection string
MONGO_DETAILS = "mongodb://basithsoftengg_db_user:62gauKQzLTyBLCE9@ac-onqwoyj-shard-00-00.ljhkmiq.mongodb.net:27017,ac-onqwoyj-shard-00-01.ljhkmiq.mongodb.net:27017,ac-onqwoyj-shard-00-02.ljhkmiq.mongodb.net:27017/?ssl=true&replicaSet=atlas-p5uwd3-shard-0&authSource=admin&appName=Cluster0"
DB_NAME = "EliteShoppe"
COLLECTION_NAME = "products"
state = {}
# Manage database connection life cycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    app.mongodb_client = AsyncIOMotorClient(MONGO_DETAILS)
    app.database = app.mongodb_client["EliteShoppe"]
    print("Connected to MongoDB!")
    state["product_cache"] = ProductCache(
        mongo_uri=MONGO_DETAILS,
        db_name=DB_NAME,
        collection_name=COLLECTION_NAME
    )
    yield
    # This runs when the server stops
    app.mongodb_client.close()
    print("MongoDB connection closed.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to Elite Shoppe App API!"}

# Example Route: Test your connection by fetching a sample list
@app.get("/products")
async def get_items():
    product_cache: ProductCache = state["product_cache"]
    
    # This returns a standard Python list of products instantly from RAM
    # No @cache decorator or .to_list() needed here anymore!
    items = product_cache.get_all_products()        
    return items

