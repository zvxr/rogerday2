import os
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.logger import get_logger

logger = get_logger("claude_service")


class ClaudeService:
    """Service for interacting with Anthropic's Claude API"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"  # Using Claude 3.5 Sonnet
        
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not found. Claude AI features will be disabled.")
            self.api_key = None
        else:
            logger.info(f"Claude AI service initialized successfully with API key: {self.api_key[:20]}...")
    
    async def generate_summary(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate a summary using Claude API
        
        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens for the response
            
        Returns:
            Generated summary text
        """
        if not self.api_key:
            logger.warning("Attempted to generate summary without API key")
            return "Claude AI is not configured. Please set the ANTHROPIC_API_KEY environment variable to enable AI-powered summaries."
        
        # Check if API key looks valid (starts with sk-ant-)
        if not self.api_key.startswith("sk-ant-"):
            logger.warning("API key format appears invalid")
            return "Invalid API key format. Please check your ANTHROPIC_API_KEY configuration."
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            logger.info(f"Calling Claude API with model {self.model}, max_tokens={max_tokens}")
            logger.debug(f"Using API key: {self.api_key[:20]}...")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info("Claude API call successful")
                return result["content"][0]["text"]
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Claude API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Claude API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise Exception(f"Error calling Claude API: {str(e)}")


# Global instance
claude_service = None


def get_claude_service() -> ClaudeService:
    """Get or create Claude service instance"""
    global claude_service
    if claude_service is None:
        claude_service = ClaudeService()
    return claude_service 