from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from app.core.config import get_settings

settings = get_settings()

client: AsyncMongoClient | None = None
database: AsyncDatabase | None = None

async def connect_to_mongo () -> None:
    global client, database
    
    client = AsyncMongoClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    await database.command("ping")
    print("CONNECTED TO MONGO")
    
async def close_mongo_connection() -> None:
    global client
    
    if client is not None:
        await client.close()
        print("CONNECTION CLOSED")
        
    
def get_database() -> AsyncDatabase:
    if database is None:
        raise RuntimeError("Database have not started")
    
    return database
