from contextlib import asynccontextmanager
from itertools import product
from elite_shoppe_app.ProductCache import ProductCache
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from functools import cache
from datetime import datetime
from fastapi import FastAPI, APIRouter, Request,Depends, HTTPException
from elite_shoppe_app.services.productService import ProductService
import logging
from pydantic import BaseModel
from typing import List

router = APIRouter();

logger = logging.getLogger(__name__)

@router.get("/prod_init")
def read_root():
    return {"message": "Welcome to Elite Shoppe App API successfully!"}

def get_product_service(request: Request) -> ProductService:
    return ProductService(
        database=request.app.database,
        cache=request.app.state.product_cache
    )

@router.get("/products")
async def get_items(request: Request):

    logger.info("get products...")
    product_cache = getattr(request.app.state, "product_cache", None)

    if not product_cache:
        raise HTTPException(
            status_code=500, 
            detail="Product cache was not initialized properly on startup."
        )

    items = product_cache.get_all_products()        
    return items

@router.put("/products/{product_id}/price")
async def update_price(
    product_id: str, 
    new_price: float, 
    service: ProductService = Depends(get_product_service)
):
    success = await service.update_product_price(product_id, new_price)

    if not success:
        raise HTTPException(status_code=404, detail="Product not found or no changes made.")
        
    return {"status": "success", "message": "Database and RAM cache updated successfully!"}

class ProductPayload(BaseModel):
    item: str
    category: str
    price: float
    brand: str
    model: str
    date: datetime

@router.put("/addProduct")
async def add_product(
    product_data: ProductPayload,
    service: ProductService = Depends(get_product_service)
):
    logger.info(f"Incoming item structure: {product_data.item}")
    product_dict = product_data.model_dump()
    success = await service.addProduct(product_dict)

    if not success:
        raise HTTPException(status_code=404, detail="Product not found or no changes made.")
        
    return {"status": "success", "message": "Database and RAM cache updated successfully!"}

@router.put("/addProducts")
async def add_products(
    product_list: List[ProductPayload],
    service: ProductService = Depends(get_product_service)
):
    
    product_dicts = [product.model_dump() for product in product_list]
    success = await service.addProducts(product_dicts)

    if not success:
        raise HTTPException(status_code=404, detail="Product not found or no changes made.")
        
    return {"status": "success", "message": "Database and RAM cache updated successfully!"}