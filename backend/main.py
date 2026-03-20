from fastapi import FastAPI, HTTPException
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

@app.get("/")
def read_root():
    return {"message": "House Price Prediction API is running"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
