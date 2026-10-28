from contextlib import asynccontextmanager
from itertools import product
from elite_shoppe_app.ProductCache import ProductCache
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from functools import cache
from datetime import datetime
from fastapi import FastAPI, APIRouter, Request, Depends, HTTPException
from elite_shoppe_app.services import userService
from elite_shoppe_app.services.addressService import AddressService
from elite_shoppe_app.services.userService import UserService
import logging
from pydantic import BaseModel
import nanoid

router = APIRouter()

logger = logging.getLogger(__name__)
custom_alphabet = "0123456789"


@router.get("/user_init")
def read_root():

    return {"message": "Welcome to Elite Shoppe App User API successfully!"}


def get_user_service(request: Request) -> UserService:
    return UserService(database=request.app.database)


class UserPayload(BaseModel):
    userId: str | None = None
    userName: str | None = None
    userEmail: str | None = None
    sex: str | None = None
    age: int | None = None


@router.post("/addUser")
async def add_user(
    user_data: UserPayload, service: UserService = Depends(get_user_service)
):
    return save_user(user_data,service)
    
    
async def save_user(user_data: UserPayload, service: UserService) -> str:
    user_dict = user_data.model_dump()
    
    clean_id = nanoid.generate(custom_alphabet, size=15)
    user_dict["_id"] = clean_id

    success = await service.addUser(user_dict)
    
    if not success:
        raise HTTPException(
            status_code=500, detail="User not found or no changes made."
        )

    return {
            "status": "save_success",            
            "userId": clean_id,
        }
    
@router.post("/add_get_user")
async def add_get_user(
    user_data: UserPayload, service: UserService = Depends(get_user_service)
):

    user_dict = user_data.model_dump()

    user = await service.get_user_by_userEmail(user_data.userEmail);
    
    if user:
        user["status"] = "user_exist"
        return user
    
    return save_user(user_data,service)

@router.get("/getAllUsers")
async def get_all_users(service: UserService = Depends(get_user_service)):

    users = await service.get_all_users()
    return users


@router.get("/getUserById/{id}")
async def get_user_by_id(id: str, service: UserService = Depends(get_user_service)):

    user = await service.get_users_by_id(id)
    return user


@router.get("/getUserByUserId/{id}")
async def get_user_by_userId(id: str, service: UserService = Depends(get_user_service)):

    user = await service.get_users_by_id(id)
    return user
