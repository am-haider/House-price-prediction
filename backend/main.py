from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
import pickle
import numpy as np
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="House Price Prediction API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.sav")
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

class HouseFeatures(BaseModel):
    bedrooms: int
    bathrooms: float
    sqft_living: float
    floors: float
    waterfront: int
    view: int
    yr_built: int

@app.post("/predict")
def predict_price(features: HouseFeatures):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        data = np.array([[
            features.bedrooms,
            features.bathrooms,
            features.sqft_living,
            features.floors,
            features.waterfront,
            features.view,
            features.yr_built
        ]])
        
        prediction = model.predict(data)
        return {"predicted_price": float(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Serve static files from the project root directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)

# On Vercel, the static files are served by Vercel directly, not by FastAPI.
if not os.environ.get("VERCEL"):
    if os.path.exists(os.path.join(project_root, "index.html")):
        app.mount("/", StaticFiles(directory=project_root, html=True), name="frontend")
    else:
        print(f"Warning: Static files (index.html) not found in {project_root}")

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server at http://127.0.0.1:8000")
    print(f"Serving frontend from: {frontend_path}")
    uvicorn.run(app, host="127.0.0.1", port=8000)
