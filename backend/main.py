from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pickle
import numpy as np
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="House Price Prediction API")

# Enable CORS for all origins (Railway serves both frontend and API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.sav")
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("Model loaded successfully.")
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


@app.get("/health")
def health_check():
    """Health check endpoint for Railway uptime monitoring."""
    return {"status": "ok", "model_loaded": model is not None}


@app.get("/ping")
def ping():
    return {"message": "pong"}


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
            features.yr_built,
        ]])
        prediction = model.predict(data)
        return {"predicted_price": float(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Serve the frontend static files
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
frontend_path = os.path.join(project_root, "frontend")

if os.path.exists(os.path.join(frontend_path, "index.html")):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"Serving frontend from: {frontend_path}")
else:
    print(f"Warning: Frontend not found at {frontend_path}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
