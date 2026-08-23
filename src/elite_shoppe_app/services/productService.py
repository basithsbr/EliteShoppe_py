from bson import ObjectId
from elite_shoppe_app.ProductCache import ProductCache
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, database: AsyncIOMotorDatabase, cache: ProductCache):
        self.db = database
        self.collection = database["products"]
        self.cache = cache

    async def update_product_price(self, product_id: str, new_price: float) -> bool:
        """Updates a product document in MongoDB and triggers a RAM cache sync."""
        # 1. Update the document in MongoDB asynchronously
        result = await self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"price": new_price}}
        )

        # 2. If the database update succeeded, refresh the RAM cache
        if result.modified_count > 0:
            self.cache.load_all_products_into_ram()
            return True
            
        return False

    async def addProducts(self, products: dict) -> bool:
        """Updates a product document in MongoDB and triggers a RAM cache sync."""
        try:
            result = await self.collection.insert_many(products)

            if result.inserted_ids and len(result.inserted_ids) > 0:
                logger.info(f"Product inserted into MongoDB with ID: {len(result.inserted_ids)}")
                
                # 3. CRITICAL: Trigger the RAM cache reload so routes see it instantly
                self.cache.reload_all_products()
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error inserting products into MongoDB: {str(e)}")
            return False


    async def addProduct(self, productString: dict) -> bool:
            """Updates a product document in MongoDB and triggers a RAM cache sync."""
            try:
                result = await self.collection.insert_one(productString)
    
                if result.inserted_id:
                    logger.info(f"Product inserted into MongoDB with ID: {result.inserted_id}")
                    
                    # 3. CRITICAL: Trigger the RAM cache reload so routes see it instantly
                    self.cache.reload_all_products()
                    return True
                    
                return False
            except Exception as e:
                logger.error(f"Error inserting product into MongoDB: {str(e)}")
                return False