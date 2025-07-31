from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import pandas as pd
import os
import uuid
import aiofiles
from datetime import datetime
from app.schemas.responses import DatasetInfo
from app.services.file_handler import FileHandler

router = APIRouter()
file_handler = FileHandler()

@router.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a dataset file (CSV, Excel, JSON)
    """
    try:
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.json']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        dataset_id = str(uuid.uuid4())
        filename = f"{dataset_id}{file_extension}"
        file_path = os.path.join("uploads", filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
        
        # Process file and get info
        dataset_info = await file_handler.process_uploaded_file(
            file_path, file.filename, dataset_id
        )
        
        return dataset_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/datasets")
async def list_datasets():
    """
    Get list of uploaded datasets
    """
    try:
        datasets = await file_handler.get_all_datasets()
        return {"datasets": datasets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve datasets: {str(e)}")

@router.get("/dataset/{dataset_id}")
async def get_dataset_info(dataset_id: str):
    """
    Get information about a specific dataset
    """
    try:
        dataset_info = await file_handler.get_dataset_info(dataset_id)
        if not dataset_info:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dataset info: {str(e)}")

@router.delete("/dataset/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """
    Delete a dataset
    """
    try:
        success = await file_handler.delete_dataset(dataset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return {"message": "Dataset deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset: {str(e)}")

@router.get("/dataset/{dataset_id}/preview")
async def preview_dataset(dataset_id: str, rows: int = 10):
    """
    Get a preview of the dataset (first N rows)
    """
    try:
        preview = await file_handler.get_dataset_preview(dataset_id, rows)
        if not preview:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return {"preview": preview, "dataset_id": dataset_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview dataset: {str(e)}")
