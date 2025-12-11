#!/usr/bin/env python3
"""
Entry point for the LLM Chatbot with RAG application.

This script serves as the main entry point to start the FastAPI server.
It properly handles module imports and provides a clean interface to run the application.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path to enable proper imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import from src
from src.main import main

if __name__ == "__main__":
    main()