from fastapi import FastAPI
from fastapi.responses import JSONResponse


# Create FastAPI instance
app = FastAPI(
    title="FastAPI RAG Application",
    description="A FastAPI application with RAG capabilities",
    version="1.0.0"
)


# Root endpoint
@app.get("/")
async def read_root():
    """
    Root endpoint that returns a welcome message
    """
    return {
        "message": "FastAPI RAG Application", 
        "status": "success",
        "version": "1.0.0"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "message": "Service is running"
    }


# Example endpoint with path parameter
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    """
    Get an item by ID with optional query parameter
    """
    return {"item_id": item_id, "q": q}


# Example POST endpoint
@app.post("/items/")
async def create_item(item: dict):
    """
    Create a new item
    """
    return {"message": "Item created", "item": item}


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    print("Starting server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )