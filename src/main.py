"""
Application entry point.

This module contains only the application initialization and server startup logic.
All FastAPI implementation details are moved to the api module.
"""

from src.api import create_app

# Initialize the FastAPI application
app = create_app()


def main():
    """
    Main function to start the application server.
    """
    import uvicorn
    
    print("Starting FastAPI RAG Application server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()