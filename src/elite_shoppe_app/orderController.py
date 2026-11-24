from contextlib import asynccontextmanager
from itertools import product
from elite_shoppe_app.ProductCache import ProductCache
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from functools import cache
from datetime import datetime
from fastapi import FastAPI, APIRouter, Request,Depends, HTTPException
from elite_shoppe_app.services.addressService import AddressService
from elite_shoppe_app.services.productService import ProductService
import logging
from pydantic import BaseModel
from typing import List
from elite_shoppe_app.services.orderService import OrderService
router = APIRouter();

logger = logging.getLogger(__name__)

@router.get("/order_init")
def read_root():
    return {"message": "Welcome to Elite Shoppe App Order API successfully!"}

def get_order_service(request: Request) -> OrderService:
    return OrderService(
        database=request.app.database
    )
    
    
class OrderPayload(BaseModel):
    userId: str | None = None    
    category: str
    model: str
    _id: str
    size: str
    qty: int
    userEmail: str
    brand: str
    price: str
    item: str
    date: str
    
    

    
@router.post("/saveOrder")
async def save_order(
    order_data: List[OrderPayload],
    service: OrderService = Depends(get_order_service)
):
    
    order_dict = [order.model_dump() for order in order_data]
    print(f"Order Data Received: {order_dict}");
    success = await service.saveOrders(order_dict)

    if not success:
        raise HTTPException(status_code=404, detail="Order not found or no changes made.")
        
    return {"status": "success", "message": "Order updated in the database successfully!"}


@router.get("/getAllOrders")
async def get_all_orders(    
    service: OrderService = Depends(get_order_service)
):
    
    success = await service.get_all_orders()

    if not success:
        raise HTTPException(status_code=404, detail="Order not found or no changes made.")
        
    return {"status": "success", "message": "Order updated in the database successfully!"}
