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

router = APIRouter();

logger = logging.getLogger(__name__)

@router.get("/address_init")
def read_root():
    return {"message": "Welcome to Elite Shoppe App Address API successfully!"}

def get_address_service(request: Request) -> AddressService:
    return AddressService(
        database=request.app.database
    )
class AddressPayload(BaseModel):
    address1: str
    address2: str
    district: str
    zip: str
    city: str
    state: str
    landMark: str
    mobile1: str
    mobile2: str
    landline: str
    email: str
    
@router.post("/addAddress")
async def add_address(
    address_data: AddressPayload,
    service: AddressService = Depends(get_address_service)
):
    
    address_dict = address_data.model_dump()
    success = await service.addAddress(address_dict)

    if not success:
        raise HTTPException(status_code=404, detail="Address not found or no changes made.")
        
    return {"status": "success", "message": "Address updated in the database successfully!"}

@router.get("/getAllAddress")
async def get_all_addresses(
    service: AddressService = Depends(get_address_service)
):
    
    
    addresses = await service.get_all_addresses()
    return addresses