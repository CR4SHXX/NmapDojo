"""
Mission generation for Nmap Dojo.
"""

import json
import re
import time
from typing import Optional
from config.constants import ALL_TOPICS, FUNDAMENTAL_TOPICS
from models.types import MissionData
from utils.logger import logger


class MissionGenerator:
    """Generates training missions using AI."""
    
    def __init__(self, model, level: int, last_topic_index: int):
        """
        Initialize the mission generator.
        
        Args:
            model: The AI model instance.
            level: Current player level.
            last_topic_index: Index of the last used topic.
        """
        self.model = model
        self.level = level
        self.last_topic_index = last_topic_index
    
    def get_next_topic(self) -> str:
        """
        Get the next topic for mission generation.
        
        Returns:
            The name of the next topic.
        """
        if self.level <= 3:
            # Fundamental topics only (Levels 1-3)
            topics = FUNDAMENTAL_TOPICS
        else:
            # All topics (Levels 4-5)
            topics = ALL_TOPICS
        
        self.last_topic_index = (self.last_topic_index + 1) % len(topics)
        return topics[self.last_topic_index]
    
    def get_difficulty(self) -> str:
        """
        Get the difficulty based on current level.
        
        Returns:
            Difficulty string (Easy/Medium/Hard/Expert).
        """
        if self.level <= 2:
            return "Easy"
        elif self.level == 3:
            return "Medium"
        elif self.level == 4:
            return "Hard"
        else:
            return "Expert"
    
    def generate_mission(self, retry: int = 0) -> Optional[MissionData]:
        """
        Generate a new mission scenario using Gemini AI.
        
        Args:
            retry: Number of retry attempts.
            
        Returns:
            MissionData dictionary or None if generation failed.
        """
        if not self.model:
            return None
        
        topic = self.get_next_topic()
        difficulty = self.get_difficulty()
        
        system_prompt = f"""You are an expert Nmap training scenario generator. Generate a realistic penetration testing scenario.

REQUIREMENTS:
- Topic: {topic}
- Difficulty: {difficulty}
- The scenario MUST require the user to use at least 2 nmap flags (3+ for Hard/Expert)
- Target IPs must be in private ranges (10.x.x.x, 192.168.x.x, 172.16.x.x for IPv4)
- For IPv6 topics, use documentation/link-local ranges (fe80::, 2001:db8::)
- For advanced topics (Level 4+), provide real-world context like 'bypass firewall', 'enumerate SMB shares', 'find CVE-vulnerable services'
- Create an engaging story/context for the scenario

OUTPUT STRICT JSON FORMAT ONLY (no markdown, no code blocks):
{{"title": "Operation Name", "description": "Detailed scenario description requiring specific nmap techniques", "target_ip": "IP address", "difficulty": "{difficulty}", "topic_category": "{topic}"}}
"""
        
        try:
            logger.info(f"Generating mission - Topic: {topic}, Difficulty: {difficulty}")
            response = self.model.generate_content(system_prompt)
            response_text = response.text.strip()
            
            # Clean up response - remove markdown code blocks if present
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            response_text = response_text.strip()
            
            logger.info(f"AI Response: {response_text}")
            
            mission: MissionData = json.loads(response_text)
            return mission
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            if retry < 2:
                time.sleep(3 * (retry + 1))
                return self.generate_mission(retry + 1)
            return None
        except Exception as e:
            logger.error(f"Mission generation error: {e}")
            if retry < 2:
                time.sleep(5 * (retry + 1))
                return self.generate_mission(retry + 1)
            raise
