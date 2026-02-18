"""
UI theme and styling utilities for Nmap Dojo.
"""

import flet as ft
from config.constants import (
    COLOR_BACKGROUND_TERMINAL,
    COLOR_BACKGROUND_PANEL,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_YELLOW,
    COLOR_TEXT_CYAN,
    FONT_MONOSPACE
)


def get_difficulty_badge_color(difficulty: str) -> str:
    """
    Get the background color for a difficulty badge.
    
    Args:
        difficulty: The difficulty level (Easy/Medium/Hard/Expert).
    
    Returns:
        Hex color code.
    """
    colors = {
        "Easy": "#28a745",
        "Medium": "#ffc107",
        "Hard": "#fd7e14",
        "Expert": "#dc3545"
    }
    return colors.get(difficulty, "#28a745")
