"""LLM generation service using Hugging Face Inference API"""
import requests
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class GeneratorService:
    """Handles text generation using Hugging Face models"""
    
    def __init__(self):
        self.api_url = settings.HF_API_URL
        self.headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"}
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """Generate text using the LLM"""
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        
        try:
            logger.info("Calling Hugging Face API...")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                generated_text = result.get('generated_text', '')
            else:
                generated_text = str(result)
            
            logger.info("Generation successful")
            return generated_text.strip()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            # Fallback to simple response
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when API fails"""
        return "I apologize, but I'm unable to generate a response at the moment. Please try again later."
    
    def generate_rag_response(
        self,
        query: str,
        context: str
    ) -> str:
        """Generate response using RAG pattern"""
        prompt = self._build_rag_prompt(query, context)
        return self.generate(prompt)
    
    def _build_rag_prompt(self, query: str, context: str) -> str:
        """Build RAG prompt template"""
        prompt = f"""<s>[INST] You are WorkWise, an AI assistant specialized in analyzing Jira project data. Answer the user's question based on the provided context.

Context:
{context}

User Question: {query}

Provide a clear, concise answer based on the context. If the context doesn't contain enough information, say so. [/INST]</s>

Answer:"""
        return prompt

# Global instance
generator = GeneratorService()