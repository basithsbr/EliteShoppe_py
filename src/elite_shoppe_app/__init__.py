from fastapi import FastAPI
from .productController import router as product_router 
from contextlib import asynccontextmanager
from itertools import product
from elite_shoppe_app.ProductCache import ProductCache
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from functools import cache
import time
from fastapi import FastAPI, APIRouter, Request, HTTPException

app = FastAPI()
# Replace this with your actual local or MongoDB Atlas connection string
MONGO_DETAILS = "mongodb://basithsoftengg_db_user:62gauKQzLTyBLCE9@ac-onqwoyj-shard-00-00.ljhkmiq.mongodb.net:27017,ac-onqwoyj-shard-00-01.ljhkmiq.mongodb.net:27017,ac-onqwoyj-shard-00-02.ljhkmiq.mongodb.net:27017/?ssl=true&replicaSet=atlas-p5uwd3-shard-0&authSource=admin&appName=Cluster0"
DB_NAME = "EliteShoppe"
COLLECTION_NAME = "products"

# Manage database connection life cycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    print("Connecting to MongoDB...")
    app.mongodb_client = AsyncIOMotorClient(MONGO_DETAILS)
    app.database = app.mongodb_client[DB_NAME]
    print("Connected to MongoDB!")
    

    cache_instance = ProductCache(
        mongo_uri=MONGO_DETAILS,    
        db_name=DB_NAME,
        collection_name=COLLECTION_NAME
    )
    app.state.product_cache = cache_instance
    print("Product cache successfully initialized!")
    
    yield
    
    # This runs when the server stops
    app.mongodb_client.close()
    print("MongoDB connection closed.")

app = FastAPI(lifespan=lifespan)

app.include_router(product_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Elite Shoppe App API main page!"}
