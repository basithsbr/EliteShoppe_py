from itertools import product

from bson import ObjectId
from elite_shoppe_app.ProductCache import ProductCache
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database["orders"]        

    async def saveOrder(self, orderString: dict) -> bool:
        """Inserts a single order document into MongoDB and triggers a RAM cache sync."""
        try:
            result = await self.collection.insert_one(orderString)

            if result.inserted_id:
                logger.info(f"Order inserted into MongoDB with ID: {result.inserted_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error inserting order into MongoDB: {str(e)}")
            return False    
    async def saveOrders(self, orderString: dict) -> bool:
            """Inserts a single order document into MongoDB and triggers a RAM cache sync."""
            try:
                result = await self.collection.insert_many(orderString)
    
                if result.inserted_ids:
                    logger.info(f"Orders inserted into MongoDB with IDs: {result.inserted_ids}")
                    return True
                
                return False
            except Exception as e:
                logger.error(f"Error inserting order into MongoDB: {str(e)}")
                return False    
        
    async def get_all_orders(self):
        logger.info(f"Fetching all orders from MongoDB")
        orders = []
        cursor = self.collection.find({})        
        raw_orders = await cursor.to_list(length=100)

        for doc in raw_orders:
            doc["_id"] = str(doc["_id"])  
            orders.append(doc)
        
        return orders                    
    
    async def get_orders_by_id(self, order_id: str):
        logger.info(f"Fetching order with ID: {order_id} from MongoDB")
        order = await self.collection.find_one({"_id": ObjectId(order_id)})

        if order:
            order["_id"] = str(order["_id"]) 
            return order
        else:
            logger.warning(f"No order found with ID: {order_id}")
            return None
        
    async def get_orders_by_userId(self, user_id: str):
        logger.info(f"Fetching order with ID: {user_id} from MongoDB")
        order = await self.collection.find_one({"userId": user_id})

        if order:
            order["_id"] = str(order["_id"]) 
            return order
        else:
            logger.warning(f"No order found with ID: {user_id}")
            return None
        
    async def update_orders_by_userId(self, orderReq: any):
        logger.info(f"update_orders_by_userId  with ID: {orderReq.userId} from MongoDB")
        order_dict = orderReq.model_dump();
        status = await self.collection.replace_one({"userId": orderReq.userId},order_dict,upsert=True)

        logger.debug(status.modified_count);
        return status.modified_count;