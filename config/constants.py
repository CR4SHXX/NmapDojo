"""
Configuration constants for Nmap Dojo.
"""

# =============================================================================
# CONSTANTS
# =============================================================================

# UI Theme Colors (Dark Mode "Hacker" Theme)
COLOR_BACKGROUND_TERMINAL = "#0d1117"  # Kali Black
COLOR_BACKGROUND_PANEL = "#161b22"     # Dark Gray
COLOR_SUCCESS = "#00ff00"              # Green for success
COLOR_ERROR = "#ff5555"                # Red for errors
COLOR_TEXT_WHITE = "#ffffff"           # White for standard text
COLOR_TEXT_YELLOW = "#ffff00"          # Yellow for hints
COLOR_TEXT_CYAN = "#00ffff"            # Cyan for info

# Fonts
FONT_MONOSPACE = "Consolas"

# AI Configuration
AI_MODEL = "gemini-2.5-flash"

# XP Values
XP_FIRST_TRY = 100
XP_ONE_HINT = 50
XP_TWO_HINTS = 25

# Level Thresholds
LEVEL_THRESHOLDS = {
    1: (0, 299),
    2: (300, 699),
    3: (700, 1199),
    4: (1200, 1999),
    5: (2000, float('inf'))
}

# Topics Configuration
FUNDAMENTAL_TOPICS = [
    "Host Discovery",
    "Port Scanning",
    "Service/OS Detection",
    "Timing/Performance",
    "Evasion",
    "Output",
    "Scripting"
]

ADVANCED_TOPICS = [
    "Firewall/IDS Bypass Advanced",
    "IPv6 Scanning",
    "NSE Script Categories",
    "Aggressive & Combo Scanning",
    "Protocol-Specific Enumeration"
]

ALL_TOPICS = FUNDAMENTAL_TOPICS + ADVANCED_TOPICS

# Max hints per mission
MAX_HINTS = 2

# Command history size
MAX_COMMAND_HISTORY = 10
