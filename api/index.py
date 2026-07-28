# Vercel Serverless Function Entry Point
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_path)

# Set up model path
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'model')
os.environ['MODEL_PATH'] = model_path

# Import the FastAPI app
from main import app

# Vercel serverless handler
from mangum import Mangum

handler = Mangum(app, lifespan="off")
