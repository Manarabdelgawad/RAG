from fastapi import FastAPI
from routes import base
from routes import data
from routes import projects
from routes import nlp
from routes.base import base_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from models.ChunkModel import ChunkModel
from models.ProjectModel import ProjectModel

app=FastAPI()


async def startup_event():
    settings=get_settings()
    app.mongo_conn=AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb_client=app.mongo_conn[settings.MONGO_DATABASE]

    # Ensure MongoDB is reachable before creating indexes
    try:
        await app.mongo_conn.admin.command("ping")
    except Exception as e:
        print(f"Warning: MongoDB is not reachable at startup: {e}")
        return

    # Initialize database indexes
    try:
        chunk_model = ChunkModel(db_client=app.mongodb_client)
        await chunk_model.create_indexes()

        project_model = ProjectModel(db_client=app.mongodb_client)
        await project_model.create_indexes()

        print("Database indexes created successfully")
    except Exception as e:
        print(f"Warning: Could not create database indexes: {e}")

async def shutdown_event():
    app.mongo_conn.close()

app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)


app.include_router(base_router)
app.include_router(data.data_router)
app.include_router(projects.project_router)
app.include_router(nlp.nlp_router)


if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
