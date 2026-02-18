"""
Type definitions for Nmap Dojo.
"""

from typing import TypedDict


class MissionData(TypedDict):
    """Type definition for mission scenario data."""
    title: str
    description: str
    target_ip: str
    difficulty: str
    topic_category: str


class ValidationResult(TypedDict):
    """Type definition for command validation result."""
    correct: bool
    feedback: str
    simulated_output: str


class ProgressData(TypedDict):
    """Type definition for user progress data."""
    xp: int
    level: int
    last_topic_index: int
    missions_completed: int
