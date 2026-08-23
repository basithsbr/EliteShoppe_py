from contextlib import asynccontextmanager
from itertools import product
from elite_shoppe_app.ProductCache import ProductCache
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from functools import cache
import time
from fastapi import FastAPI, APIRouter, Request, HTTPException

router = APIRouter();


@router.get("/prod_init")
def read_root():
    return {"message": "Welcome to Elite Shoppe App API successfully!"}

# Example Route: Test your connection by fetching a sample list
@router.get("/products")
async def get_items(request: Request):
    # product_cache: ProductCache = state["product_cache"]
    product_cache = getattr(request.app.state, "product_cache", None)

    if not product_cache:
        raise HTTPException(
            status_code=500, 
            detail="Product cache was not initialized properly on startup."
        )

    items = product_cache.get_all_products()        
    return items


