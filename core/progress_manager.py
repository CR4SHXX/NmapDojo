"""
Progress management for Nmap Dojo.
"""

import json
from pathlib import Path
from config.settings import PROGRESS_FILE
from config.constants import LEVEL_THRESHOLDS
from models.types import ProgressData
from utils.logger import logger


class ProgressManager:
    """Manages user progress (XP, level, missions completed)."""
    
    def __init__(self):
        """Initialize the progress manager."""
        self.xp: int = 0
        self.level: int = 1
        self.last_topic_index: int = -1
        self.missions_completed: int = 0
    
    def load_progress(self) -> ProgressData:
        """
        Load user progress from the JSON file.
        
        Returns:
            The loaded progress data.
        """
        try:
            if Path(PROGRESS_FILE).exists():
                with open(PROGRESS_FILE, 'r') as f:
                    data: ProgressData = json.load(f)
                    self.xp = data.get('xp', 0)
                    self.level = data.get('level', 1)
                    self.last_topic_index = data.get('last_topic_index', -1)
                    self.missions_completed = data.get('missions_completed', 0)
                    logger.info(f"Progress loaded: XP={self.xp}, Level={self.level}")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load progress: {e}")
        
        return {
            'xp': self.xp,
            'level': self.level,
            'last_topic_index': self.last_topic_index,
            'missions_completed': self.missions_completed
        }
    
    def save_progress(self, data: ProgressData) -> None:
        """
        Save user progress to the JSON file.
        
        Args:
            data: The progress data to save.
        """
        try:
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Progress saved")
        except IOError as e:
            logger.error(f"Could not save progress: {e}")
    
    def calculate_level(self, xp: int) -> int:
        """
        Calculate the current level based on XP.
        
        Args:
            xp: The current XP amount.
        
        Returns:
            The calculated level (1-5).
        """
        for level, (min_xp, max_xp) in LEVEL_THRESHOLDS.items():
            if min_xp <= xp <= max_xp:
                return level
        return 5
