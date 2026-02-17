"""
AI service integration for Nmap Dojo.
"""

import warnings
# Suppress deprecation warning for google.generativeai (still functional)
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import google.generativeai as genai

from typing import Optional
from config.constants import AI_MODEL
from config.settings import GEMINI_API_KEY
from models.types import MissionData
from utils.logger import logger


class AIService:
    """Manages AI interactions with Google Gemini."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.api_key: Optional[str] = None
        self.model: Optional[genai.GenerativeModel] = None
    
    def initialize_api(self, api_key: Optional[str] = None) -> bool:
        """
        Initialize the Google Gemini API.
        
        Args:
            api_key: Optional API key to use. If not provided, uses default from settings.
        
        Returns:
            True if initialization succeeded, False otherwise.
        """
        self.api_key = api_key if api_key else GEMINI_API_KEY
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(AI_MODEL)
            logger.info("AI Engine configured successfully")
            return True
        except Exception as e:
            logger.error(f"API configuration failed: {e}")
            return False
    
    def get_hint(self, current_mission: MissionData) -> str:
        """
        Get a hint for the current mission.
        
        Args:
            current_mission: The current mission data.
        
        Returns:
            Hint text.
        
        Raises:
            Exception if hint generation fails.
        """
        if not self.model:
            raise Exception("AI model not initialized")
        
        prompt = f"""Provide a helpful hint for this nmap scenario without giving the full answer:

Mission: {current_mission['title']}
Description: {current_mission['description']}
Target: {current_mission['target_ip']}
Topic: {current_mission['topic_category']}

Give ONE specific hint about which nmap flag or technique to use. Be helpful but don't reveal the full command."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Hint generation error: {e}")
            raise
    
    def get_full_answer(self, current_mission: MissionData) -> str:
        """
        Get the full answer for the current mission.
        
        Args:
            current_mission: The current mission data.
        
        Returns:
            Full answer text with command and explanation.
        
        Raises:
            Exception if answer generation fails.
        """
        if not self.model:
            raise Exception("AI model not initialized")
        
        prompt = f"""Provide the correct nmap command for this scenario:

Mission: {current_mission['title']}
Description: {current_mission['description']}
Target: {current_mission['target_ip']}
Topic: {current_mission['topic_category']}

Give the complete nmap command and briefly explain why each flag is used."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Answer generation error: {e}")
            raise
    
    def get_explanation(self, current_mission: MissionData) -> str:
        """
        Get an explanation for why the last command was incorrect.
        
        Args:
            current_mission: The current mission data.
        
        Returns:
            Explanation text.
        
        Raises:
            Exception if explanation generation fails.
        """
        if not self.model:
            raise Exception("AI model not initialized")
        
        prompt = f"""Explain why the user's last command was incorrect for this scenario:

Mission: {current_mission['title']}
Description: {current_mission['description']}
Target: {current_mission['target_ip']}
Topic: {current_mission['topic_category']}

Explain what was wrong and what the correct approach should be. Be educational and helpful."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Explanation generation error: {e}")
            raise
