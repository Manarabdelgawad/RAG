from fastapi import FastAPI
from routes import base, data, projects
from routes.base import base_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from models.ChunkModel import ChunkModel
from models.ProjectModel import ProjectModel
from stores.llm.LLMFactory import LLMFactory
from stores.VectorDB.VectorDBProvideFactory import VectorDBProviderFactory
from routes.metrics import setup_metrics  

app = FastAPI()

# Prometheus metrics middleware
setup_metrics(app)


async def startup_event():
    settings = get_settings()

    # Connect to MongoDB
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb_client = app.mongo_conn[settings.MONGO_DATABASE]

    try:
        await app.mongo_conn.admin.command("ping")
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"Warning: MongoDB not reachable: {e}")
        return

    # Create necessary indexes
    try:
        chunk_model = ChunkModel(db_client=app.mongodb_client)
        await chunk_model.create_indexes()

        project_model = ProjectModel(db_client=app.mongodb_client)
        await project_model.create_indexes()

        print("MongoDB indexes created successfully")
    except Exception as e:
        print(f"Warning: Could not create indexes: {e}")

    # initialize LLM
    llm_factory = LLMFactory(settings)
    app.llm_client = llm_factory.create(provider=settings.GENERATION_BACKEND)
    app.llm_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Initialize Qdrant
    vectordb_factory = VectorDBProviderFactory(config=settings, db_client=app.mongodb_client)
    app.vectordb_client = vectordb_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await app.vectordb_client.connect()

    print("Qdrant connected successfully")


async def shutdown_event():
    print("Shutting down connections...")
    app.mongo_conn.close()
    await app.vectordb_client.disconnect()


app.router.lifespan.on_startup.append(startup_event)
app.router.lifespan.on_shutdown.append(shutdown_event)

app.include_router(base_router)
app.include_router(data.data_router)
app.include_router(projects.project_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=4)
