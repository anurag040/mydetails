"""
Unified LLM Service supporting both OpenAI and Google Gemini models
"""
import os
import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import json

# LLM imports
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    try:
        import openai
        OpenAI = openai.OpenAI if hasattr(openai, 'OpenAI') else None
        OPENAI_AVAILABLE = OpenAI is not None
    except ImportError:
        OpenAI = None
        OPENAI_AVAILABLE = False
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

class LLMModel(str, Enum):
    # OpenAI models
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Gemini models
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"

class UnifiedLLMService:
    """Unified service for interacting with multiple LLM providers"""
    
    def __init__(self):
        """Initialize the unified LLM service with API clients"""
        self.openai_client = None
        self.gemini_client = None
        
        # Initialize OpenAI client (only if package is available)
        if OPENAI_AVAILABLE:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                try:
                    self.openai_client = OpenAI(api_key=openai_api_key)
                    logger.info("OpenAI client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {e}")
            else:
                logger.warning("OPENAI_API_KEY not found in environment variables")
        else:
            logger.warning("OpenAI package not available. Install with: pip install openai")
        
        # Initialize Gemini client (only if package is available)
        if GEMINI_AVAILABLE:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                try:
                    genai.configure(api_key=gemini_api_key)
                    self.gemini_client = genai.GenerativeModel('gemini-pro')
                    logger.info("Gemini client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Gemini client: {e}")
            else:
                logger.warning("GEMINI_API_KEY not found in environment variables")
        else:
            logger.warning("Google Generative AI package not available. Install with: pip install google-generativeai==0.3.2")
    
    def get_provider_from_model(self, model: str) -> LLMProvider:
        """Determine provider from model name"""
        if model.startswith("gpt"):
            return LLMProvider.OPENAI
        elif model.startswith("gemini"):
            return LLMProvider.GEMINI
        else:
            raise ValueError(f"Unknown model: {model}")
    
    def is_model_available(self, model: str) -> bool:
        """Check if a model is available"""
        provider = self.get_provider_from_model(model)
        
        if provider == LLMProvider.OPENAI:
            return OPENAI_AVAILABLE and self.openai_client is not None
        elif provider == LLMProvider.GEMINI:
            return GEMINI_AVAILABLE and self.gemini_client is not None
        
        return False
    
    async def generate_completion(
        self,
        prompt: str,
        model: str = LLMModel.GPT_4O_MINI,
        max_tokens: int = 1000,
        temperature: float = 0.3,
        messages: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate completion using specified model"""
        
        if not self.is_model_available(model):
            available_models = self.get_available_models()
            if available_models:
                fallback_model = available_models[0]
                logger.warning(f"Model {model} not available, falling back to {fallback_model}")
                model = fallback_model
            else:
                raise RuntimeError("No LLM models available. Please configure API keys.")
        
        provider = self.get_provider_from_model(model)
        
        try:
            if provider == LLMProvider.OPENAI:
                return await self._generate_openai_completion(
                    prompt, model, max_tokens, temperature, messages
                )
            elif provider == LLMProvider.GEMINI:
                return await self._generate_gemini_completion(
                    prompt, model, max_tokens, temperature
                )
        except Exception as e:
            logger.error(f"Error generating completion with {model}: {e}")
            return f"Error generating response: {str(e)}"
    
    async def _generate_openai_completion(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        messages: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate completion using OpenAI"""
        try:
            if messages:
                # Use provided messages for chat format
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            else:
                # Use simple prompt
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_gemini_completion(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate completion using Gemini"""
        try:
            # Create model instance
            gemini_model = genai.GenerativeModel(model)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=0.8,
                top_k=40
            )
            
            # Generate content
            response = gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        available = []
        
        if OPENAI_AVAILABLE and self.openai_client:
            available.extend([
                LLMModel.GPT_4O_MINI,
                LLMModel.GPT_4_TURBO,
                LLMModel.GPT_3_5_TURBO
            ])
        
        if GEMINI_AVAILABLE and self.gemini_client:
            available.extend([
                LLMModel.GEMINI_PRO,
                LLMModel.GEMINI_PRO_VISION
            ])
        
        return available
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        return {
            "available_models": self.get_available_models(),
            "providers": {
                "openai": {
                    "available": OPENAI_AVAILABLE and self.openai_client is not None,
                    "models": [LLMModel.GPT_4O_MINI, LLMModel.GPT_4_TURBO, LLMModel.GPT_3_5_TURBO]
                },
                "gemini": {
                    "available": GEMINI_AVAILABLE and self.gemini_client is not None,
                    "models": [LLMModel.GEMINI_PRO, LLMModel.GEMINI_PRO_VISION]
                }
            },
            "default_model": LLMModel.GPT_4O_MINI if (OPENAI_AVAILABLE and self.openai_client) else (
                LLMModel.GEMINI_PRO if (GEMINI_AVAILABLE and self.gemini_client) else None
            )
        }

# Global instance
unified_llm_service = UnifiedLLMService()
