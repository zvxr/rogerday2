import os
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings


class ClaudeService:
    """Service for interacting with Anthropic's Claude API"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"  # Using Claude 3.5 Sonnet
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    async def generate_summary(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate a summary using Claude API
        
        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens for the response
            
        Returns:
            Generated summary text
        """
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
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result["content"][0]["text"]
                
        except httpx.HTTPStatusError as e:
            raise Exception(f"Claude API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Error calling Claude API: {str(e)}")


# Global instance
claude_service = None


def get_claude_service() -> ClaudeService:
    """Get or create Claude service instance"""
    global claude_service
    if claude_service is None:
        claude_service = ClaudeService()
    return claude_service 