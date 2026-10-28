from itertools import product

from bson import ObjectId
from elite_shoppe_app.ProductCache import ProductCache
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database["users"]        

    async def update_user(self, user_id: str, new_user: dict) -> bool:
        """Updates a user document in MongoDB and triggers a RAM cache sync."""
        # 1. Update the document in MongoDB asynchronously
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"name": new_user.get("name"), "email": new_user.get("email")}}
        )

        # 2. If the database update succeeded, refresh the RAM cache
        if result.modified_count > 0:
            self.cache.load_all_products_into_ram()
            return True
            
        return False

    async def addUsers(self, users: list) -> bool:
        """Inserts multiple user documents into MongoDB and triggers a RAM cache sync."""
        try:
            result = await self.collection.insert_many(users)

            if result.inserted_ids and len(result.inserted_ids) > 0:
                logger.info(f"User inserted into MongoDB with ID: {len(result.inserted_ids)}")
                
                # 3. CRITICAL: Trigger the RAM cache reload so routes see it instantly
                self.cache.reload_all_products()
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error inserting users into MongoDB: {str(e)}")
            return False

    async def addUser(self, userInputReq: dict) -> bool:
        """Inserts a single user document into MongoDB and triggers a RAM cache sync."""
        try:            
            result = await self.collection.insert_one(userInputReq)

            if result.inserted_id:
                logger.info(f"User inserted into MongoDB with ID: {result.inserted_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error inserting user into MongoDB: {str(e)}")
            return False    
        
    async def get_all_users(self):
        logger.info(f"Fetching all users from MongoDB")
        users = []
        cursor = self.collection.find({})        
        raw_users = await cursor.to_list(length=100)

        for doc in raw_users:
            doc["_id"] = str(doc["_id"])  
            users.append(doc)
        
        return users                    
    
    async def get_users_by_id(self, user_id: str):
        logger.info(f"Fetching user with ID: {user_id} from MongoDB")
        user = await self.collection.find_one({"_id": ObjectId(user_id)})

        if user:
            user["_id"] = str(user["_id"]) 
            return user
        else:
            logger.warning(f"No user found with ID: {user_id}")
            return None
        
    async def get_users_by_userId(self, user_id: str):
            
            logger.info(f"Fetching user with ID: {user_id} from MongoDB")
            user = await self.collection.find_one({"id": ObjectId(user_id)})
    
            if user:
                user["_id"] = str(user["_id"]) 
                return user
            else:
                logger.warning(f"No user found with ID: {user_id}")
                return None
            
    async def get_user_by_userEmail(self, user_email: str):                
            logger.info(f"Fetching user with user_email: {user_email} from MongoDB")
            user = await self.collection.find_one({"userEmail": user_email})
    
            if user:
                user["_id"] = str(user["_id"]) 
                return user
            else:
                logger.warning(f"No user found with ID: {user_email}")
                return None