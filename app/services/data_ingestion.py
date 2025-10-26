"""Data ingestion service for parsing Jira exports"""
import pandas as pd
import json
from typing import List, Dict, Any
from pathlib import Path
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class DataIngestionService:
    """Handles parsing and preprocessing of Jira data files"""
    
    @staticmethod
    def parse_csv(file_path: str) -> List[Dict[str, Any]]:
        """Parse Jira CSV export"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} records from {file_path}")
            
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            # Convert to list of dictionaries
            records = df.to_dict('records')
            
            # Clean and structure data
            processed_records = []
            for record in records:
                processed = DataIngestionService._clean_record(record)
                processed_records.append(processed)
            
            return processed_records
        
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            raise
    
    @staticmethod
    def parse_json(file_path: str) -> List[Dict[str, Any]]:
        """Parse Jira JSON export"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, dict) and 'issues' in data:
                records = data['issues']
            elif isinstance(data, list):
                records = data
            else:
                raise ValueError("Unexpected JSON structure")
            
            logger.info(f"Loaded {len(records)} records from {file_path}")
            return [DataIngestionService._clean_record(r) for r in records]
        
        except Exception as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            raise
    
    @staticmethod
    def _clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize a single record"""
        # Handle missing values
        for key, value in record.items():
            if pd.isna(value) or value == '' or value == 'None':
                record[key] = None
        
        # Create searchable text representation
        text_fields = ['summary', 'description', 'status', 'priority', 'project']
        text_parts = []
        
        for field in text_fields:
            if field in record and record[field]:
                text_parts.append(f"{field}: {record[field]}")
        
        record['searchable_text'] = " | ".join(text_parts)
        
        return record
    
    @staticmethod
    def load_data(file_path: str) -> List[Dict[str, Any]]:
        """Load data from file (auto-detect format)"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.csv':
            return DataIngestionService.parse_csv(file_path)
        elif file_ext == '.json':
            return DataIngestionService.parse_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
