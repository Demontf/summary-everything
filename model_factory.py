from typing import List, Dict, Any
import os

from qwen import summary_papers as summary_papers_qwen
from claude import summary_papers_claude
from config import MODEL_CONFIGS

class ModelFactory:
    @staticmethod
    def get_model_type() -> str:
        """Get the model type from environment variable or default to Qwen"""
        return os.getenv("SUMMARY_MODEL_TYPE", "qwen")
    
    @staticmethod
    def summary_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Route the summary request to the appropriate model"""
        model_type = ModelFactory.get_model_type()
        
        if model_type not in MODEL_CONFIGS:
            raise ValueError(f"Unsupported model type: {model_type}")
            
        if model_type == "qwen":
            return summary_papers_qwen(papers)
        elif model_type == "claude":
            return summary_papers_claude(papers)
        else:
            raise ValueError(f"No implementation found for model type: {model_type}")