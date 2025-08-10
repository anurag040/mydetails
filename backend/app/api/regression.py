from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import os
import numpy as np

router = APIRouter()

class RegressionRequest(BaseModel):
    dataset_id: str
    x_column: str
    y_column: str

@router.post("/advanced/regression")
async def regression_analysis(request: RegressionRequest):
    """
    Perform linear regression analysis on a dataset using specified X and Y columns.
    Returns regression coefficients, intercept, R², MSE, and MAE.
    """
    try:
        # Load the dataset
        dataset_path = f"uploads/{request.dataset_id}.csv"
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        df = pd.read_csv(dataset_path)
        
        # Check if columns exist
        if request.x_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"X column '{request.x_column}' not found in data")
        if request.y_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Y column '{request.y_column}' not found in data")
        
        # Prepare data
        X = df[[request.x_column]].copy()
        y = df[request.y_column].copy()
        
        # Check for numeric data
        if not pd.api.types.is_numeric_dtype(X[request.x_column]):
            raise HTTPException(status_code=400, detail=f"X column '{request.x_column}' must be numeric")
        if not pd.api.types.is_numeric_dtype(y):
            raise HTTPException(status_code=400, detail=f"Y column '{request.y_column}' must be numeric")
        
        # Remove rows with missing values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        if len(X) < 2:
            raise HTTPException(status_code=400, detail="Not enough valid data points for regression")
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Fit the model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Calculate metrics
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_mse = mean_squared_error(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        result = {
            "metrics": {
                "r2_score": float(test_r2),
                "train_r2_score": float(train_r2),
                "mse": float(test_mse),
                "train_mse": float(train_mse),
                "mae": float(test_mae),
                "train_mae": float(train_mae)
            },
            "model_parameters": {
                "coefficient": float(model.coef_[0]),
                "intercept": float(model.intercept_)
            },
            "feature_importance": {
                request.x_column: abs(float(model.coef_[0]))
            },
            "data_info": {
                "n_samples": len(X),
                "n_train": len(X_train),
                "n_test": len(X_test),
                "x_column": request.x_column,
                "y_column": request.y_column
            },
            "equation": f"{request.y_column} = {float(model.coef_[0]):.4f} * {request.x_column} + {float(model.intercept_):.4f}"
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
