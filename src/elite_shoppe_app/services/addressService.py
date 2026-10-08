from bson import ObjectId
from elite_shoppe_app.ProductCache import ProductCache
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class AddressService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database["addresses"]        

    async def update_address(self, address_id: str, new_address: dict) -> bool:
        """Updates an address document in MongoDB and triggers a RAM cache sync."""
        # 1. Update the document in MongoDB asynchronously
        result = await self.collection.update_one(
            {"_id": ObjectId(address_id)},
            {"$set": {"address1": new_address.get("address1"), "address2": new_address.get("address2")}}
        )

        # 2. If the database update succeeded, refresh the RAM cache
        if result.modified_count > 0:
            self.cache.load_all_products_into_ram()
            return True
            
        return False

    async def addAddresses(self, addresses: list) -> bool:
        """Inserts multiple address documents into MongoDB and triggers a RAM cache sync."""
        try:
            result = await self.collection.insert_many(addresses)

            if result.inserted_ids and len(result.inserted_ids) > 0:
                logger.info(f"Address inserted into MongoDB with ID: {len(result.inserted_ids)}")
                
                # 3. CRITICAL: Trigger the RAM cache reload so routes see it instantly
                self.cache.reload_all_products()
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error inserting addresses into MongoDB: {str(e)}")
            return False

    async def addAddress(self, addressString: dict) -> bool:
        """Inserts a single address document into MongoDB and triggers a RAM cache sync."""
        try:
            result = await self.collection.insert_one(addressString)

            if result.inserted_id:
                logger.info(f"Address inserted into MongoDB with ID: {result.inserted_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error inserting address into MongoDB: {str(e)}")
            return False    
        
    async def get_all_addresses(self):
        logger.info(f"Fetching all addresses from MongoDB")
        addresses = []
        async for doc in self.collection.find():
            logger.info(f"Fetched address: {doc}")
            addresses.append(doc)
        return addresses                    