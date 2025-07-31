import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.schemas.responses import DatasetInfo

class FileHandler:
    def __init__(self):
        self.upload_dir = "uploads"
        self.metadata_file = os.path.join(self.upload_dir, "metadata.json")
        self.ensure_upload_dir()
    
    def ensure_upload_dir(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    async def process_uploaded_file(self, file_path: str, original_filename: str, dataset_id: str) -> DatasetInfo:
        """Process uploaded file and extract metadata"""
        try:
            # Read the file based on extension
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_extension == '.json':
                df = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Calculate missing data ratio
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isnull().sum().sum()
            missing_ratio = missing_cells / total_cells if total_cells > 0 else 0
            
            # Create dataset info
            dataset_info = DatasetInfo(
                dataset_id=dataset_id,
                filename=original_filename,
                size=os.path.getsize(file_path),
                rows=df.shape[0],
                columns=df.shape[1],
                column_names=df.columns.tolist(),
                data_types={col: str(dtype) for col, dtype in df.dtypes.items()},
                missing_data_ratio=missing_ratio,
                upload_timestamp=datetime.now()
            )
            
            # Save metadata
            await self.save_dataset_metadata(dataset_id, dataset_info, file_path)
            
            return dataset_info
            
        except Exception as e:
            # Clean up file if processing fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
    
    async def save_dataset_metadata(self, dataset_id: str, dataset_info: DatasetInfo, file_path: str):
        """Save dataset metadata to JSON file"""
        metadata = {}
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
        
        metadata[dataset_id] = {
            **dataset_info.dict(),
            "file_path": file_path,
            "upload_timestamp": dataset_info.upload_timestamp.isoformat()
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    async def get_dataset_info(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset information by ID"""
        if not os.path.exists(self.metadata_file):
            return None
        
        with open(self.metadata_file, 'r') as f:
            metadata = json.load(f)
        
        return metadata.get(dataset_id)
    
    async def get_all_datasets(self) -> List[Dict[str, Any]]:
        """Get all datasets metadata"""
        if not os.path.exists(self.metadata_file):
            return []
        
        with open(self.metadata_file, 'r') as f:
            metadata = json.load(f)
        
        return list(metadata.values())
    
    async def delete_dataset(self, dataset_id: str) -> bool:
        """Delete dataset and its metadata"""
        if not os.path.exists(self.metadata_file):
            return False
        
        with open(self.metadata_file, 'r') as f:
            metadata = json.load(f)
        
        if dataset_id not in metadata:
            return False
        
        # Delete file
        file_path = metadata[dataset_id].get('file_path')
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from metadata
        del metadata[dataset_id]
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True
    
    async def get_dataset_preview(self, dataset_id: str, rows: int = 10) -> Optional[Dict[str, Any]]:
        """Get dataset preview"""
        dataset_info = await self.get_dataset_info(dataset_id)
        if not dataset_info:
            return None
        
        file_path = dataset_info['file_path']
        if not os.path.exists(file_path):
            return None
        
        try:
            # Read the file
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file_path, nrows=rows)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=rows)
            elif file_extension == '.json':
                df = pd.read_json(file_path)
                df = df.head(rows)
            else:
                return None
            
            return {
                "data": df.to_dict('records'),
                "columns": df.columns.tolist(),
                "total_rows": dataset_info['rows'],
                "preview_rows": len(df)
            }
            
        except Exception:
            return None
    
    async def load_dataset(self, dataset_id: str) -> Optional[pd.DataFrame]:
        """Load complete dataset as DataFrame"""
        dataset_info = await self.get_dataset_info(dataset_id)
        if not dataset_info:
            return None
        
        file_path = dataset_info['file_path']
        if not os.path.exists(file_path):
            return None
        
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                return pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            elif file_extension == '.json':
                return pd.read_json(file_path)
            else:
                return None
                
        except Exception:
            return None
