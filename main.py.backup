#!/usr/bin/env python3
"""
Nmap Dojo - An AI-Powered Nmap Training Desktop Application

A robust, crash-proof desktop application using Python and Flet that trains
users on nmap commands. Uses Google Gemini 1.5 Pro as the game engine to
generate scenarios and validate answers.

Author: Nmap Dojo Team
"""

import flet as ft
import warnings
# Suppress deprecation warning for google.generativeai (still functional)
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import google.generativeai as genai
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import TypedDict, Optional, List

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
GEMINI_API_KEY = "AIzaSyDoP-j4RFx25h3rlU_8CqJpcbxN-OXAZms"

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

# Progress File
PROGRESS_FILE = "dojo_progress.json"
LOG_FILE = "dojo.log"

# Max hints per mission
MAX_HINTS = 2

# Command history size
MAX_COMMAND_HISTORY = 10

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

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


# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================

class NmapDojoApp:
    """
    Main application class for Nmap Dojo training app.
    
    This class manages the entire application state, UI, and AI interactions.
    It provides a split-screen layout with a terminal on the left and mission
    control panel on the right.
    """
    
    def __init__(self, page: ft.Page) -> None:
        """
        Initialize the Nmap Dojo application.
        
        Args:
            page: The Flet page object for the application.
        """
        self.page = page
        self.api_key: Optional[str] = None
        self.model: Optional[genai.GenerativeModel] = None
        
        # Progress state
        self.xp: int = 0
        self.level: int = 1
        self.last_topic_index: int = -1
        self.missions_completed: int = 0
        
        # Mission state
        self.current_mission: Optional[MissionData] = None
        self.hints_used: int = 0
        self.mission_completed: bool = False
        
        # Command history
        self.command_history: List[str] = []
        self.history_index: int = -1
        
        # UI Components (initialized in setup_ui)
        self.terminal_output: Optional[ft.ListView] = None
        self.command_input: Optional[ft.TextField] = None
        self.xp_text: Optional[ft.Text] = None
        self.level_text: Optional[ft.Text] = None
        self.mission_title: Optional[ft.Text] = None
        self.mission_description: Optional[ft.Text] = None
        self.mission_target: Optional[ft.Text] = None
        self.mission_difficulty: Optional[ft.Container] = None
        self.hint_counter: Optional[ft.Text] = None
        self.new_mission_btn: Optional[ft.ElevatedButton] = None
        self.get_hint_btn: Optional[ft.ElevatedButton] = None
        self.explain_btn: Optional[ft.ElevatedButton] = None
        self.loading_indicator: Optional[ft.ProgressRing] = None
        self.api_key_banner: Optional[ft.Container] = None
        self.api_key_input: Optional[ft.TextField] = None
        
        # Setup
        self.setup_page()
        self.load_progress()
        self.setup_ui()
        self.initialize_api()
    
    def setup_page(self) -> None:
        """Configure the main page settings."""
        self.page.title = "Nmap Dojo - AI-Powered Training"
        self.page.bgcolor = COLOR_BACKGROUND_TERMINAL
        self.page.padding = 0
        self.page.spacing = 0
        self.page.window.min_width = 1024
        self.page.window.min_height = 768
        self.page.on_keyboard_event = self.on_key_down
    
    def load_progress(self) -> None:
        """Load user progress from the JSON file."""
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
    
    def save_progress(self) -> None:
        """Save user progress to the JSON file."""
        try:
            data: ProgressData = {
                'xp': self.xp,
                'level': self.level,
                'last_topic_index': self.last_topic_index,
                'missions_completed': self.missions_completed
            }
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Progress saved")
        except IOError as e:
            logger.error(f"Could not save progress: {e}")
    
    def calculate_level(self) -> int:
        """
        Calculate the current level based on XP.
        
        Returns:
            The calculated level (1-5).
        """
        for level, (min_xp, max_xp) in LEVEL_THRESHOLDS.items():
            if min_xp <= self.xp <= max_xp:
                return level
        return 5
    
    def setup_ui(self) -> None:
        """Set up the main UI components."""
        # Terminal output area
        self.terminal_output = ft.ListView(
            expand=True,
            spacing=2,
            padding=10,
            auto_scroll=True
        )
        
        # Command input field
        self.command_input = ft.TextField(
            prefix=ft.Text("> ", color=COLOR_SUCCESS, font_family=FONT_MONOSPACE),
            hint_text="Enter nmap command...",
            border_color=COLOR_SUCCESS,
            focused_border_color=COLOR_TEXT_CYAN,
            bgcolor=COLOR_BACKGROUND_TERMINAL,
            color=COLOR_SUCCESS,
            cursor_color=COLOR_SUCCESS,
            text_style=ft.TextStyle(font_family=FONT_MONOSPACE),
            expand=True,
            on_submit=self.on_command_submit
        )
        
        # Loading indicator
        self.loading_indicator = ft.ProgressRing(
            width=20,
            height=20,
            stroke_width=2,
            color=COLOR_SUCCESS,
            visible=False
        )
        
        # Stats bar
        self.xp_text = ft.Text(
            f"XP: {self.xp}",
            color=COLOR_TEXT_CYAN,
            size=16,
            weight=ft.FontWeight.BOLD
        )
        self.level_text = ft.Text(
            f"Level: {self.level}",
            color=COLOR_SUCCESS,
            size=16,
            weight=ft.FontWeight.BOLD
        )
        
        stats_bar = ft.Row(
            [self.xp_text, self.level_text],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Mission card components
        self.mission_title = ft.Text(
            "Loading Mission...",
            color=COLOR_TEXT_WHITE,
            size=18,
            weight=ft.FontWeight.BOLD
        )
        
        self.mission_description = ft.Text(
            "Please wait while the mission is generated...",
            color=COLOR_TEXT_WHITE,
            size=14
        )
        
        self.mission_target = ft.Text(
            "Target: N/A",
            color=COLOR_TEXT_CYAN,
            size=14,
            weight=ft.FontWeight.BOLD
        )
        
        self.mission_difficulty = ft.Container(
            content=ft.Text("Easy", color=COLOR_TEXT_WHITE, size=12),
            bgcolor="#28a745",
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=10
        )
        
        self.hint_counter = ft.Text(
            f"Hints Used: 0/{MAX_HINTS}",
            color=COLOR_TEXT_YELLOW,
            size=12
        )
        
        # Mission card container
        mission_card = ft.Container(
            content=ft.Column([
                self.mission_title,
                ft.Divider(color=COLOR_TEXT_WHITE, height=1),
                self.mission_description,
                ft.Row([self.mission_target, self.mission_difficulty], 
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.hint_counter
            ], spacing=10),
            bgcolor="#1f2937",
            padding=15,
            border_radius=10,
            margin=ft.margin.only(bottom=10)
        )
        
        # Action buttons
        self.new_mission_btn = ft.ElevatedButton(
            "New Mission",
            icon=ft.Icons.REFRESH,
            bgcolor=COLOR_SUCCESS,
            color=COLOR_BACKGROUND_TERMINAL,
            on_click=self.on_new_mission
        )
        
        self.get_hint_btn = ft.ElevatedButton(
            "Get Hint",
            icon=ft.Icons.LIGHTBULB,
            bgcolor=COLOR_TEXT_YELLOW,
            color=COLOR_BACKGROUND_TERMINAL,
            on_click=self.on_get_hint
        )
        
        self.explain_btn = ft.ElevatedButton(
            "Explain Why",
            icon=ft.Icons.HELP,
            bgcolor=COLOR_ERROR,
            color=COLOR_TEXT_WHITE,
            visible=False,
            on_click=self.on_explain_why
        )
        
        buttons_row = ft.Row(
            [self.new_mission_btn, self.get_hint_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True
        )
        
        # API Key input banner
        self.api_key_input = ft.TextField(
            label="Enter Gemini API Key",
            password=True,
            can_reveal_password=True,
            border_color=COLOR_TEXT_CYAN,
            focused_border_color=COLOR_SUCCESS,
            bgcolor=COLOR_BACKGROUND_PANEL,
            color=COLOR_TEXT_WHITE,
            expand=True
        )
        
        self.api_key_banner = ft.Container(
            content=ft.Column([
                ft.Text(
                    "⚠️ API Key Required",
                    color=COLOR_TEXT_YELLOW,
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Please enter your Google Gemini API key to start training.",
                    color=COLOR_TEXT_WHITE,
                    size=12
                ),
                ft.Row([
                    self.api_key_input,
                    ft.ElevatedButton(
                        "Connect",
                        bgcolor=COLOR_SUCCESS,
                        color=COLOR_BACKGROUND_TERMINAL,
                        on_click=self.on_api_key_submit
                    )
                ])
            ], spacing=10),
            bgcolor=COLOR_BACKGROUND_PANEL,
            padding=15,
            border_radius=10,
            visible=False
        )
        
        # Left Panel (Terminal - 70%)
        left_panel = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(
                        "NMAP DOJO TERMINAL",
                        color=COLOR_SUCCESS,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        font_family=FONT_MONOSPACE
                    ),
                    padding=10,
                    bgcolor=COLOR_BACKGROUND_PANEL
                ),
                ft.Container(
                    content=self.terminal_output,
                    expand=True,
                    bgcolor=COLOR_BACKGROUND_TERMINAL,
                    padding=5
                ),
                ft.Container(
                    content=ft.Row([
                        self.command_input,
                        self.loading_indicator
                    ]),
                    padding=10,
                    bgcolor=COLOR_BACKGROUND_PANEL
                )
            ], spacing=0, expand=True),
            bgcolor=COLOR_BACKGROUND_TERMINAL,
            expand=7  # 70% of the row
        )
        
        # Right Panel (Mission Control - 30%)
        right_panel = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(
                        "MISSION CONTROL",
                        color=COLOR_TEXT_CYAN,
                        size=14,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=10,
                    bgcolor="#1a1f25"
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=[
                            stats_bar,
                            ft.Divider(color=COLOR_TEXT_WHITE, height=1),
                            mission_card,
                            buttons_row,
                            self.explain_btn,
                            self.api_key_banner
                        ],
                        spacing=15,
                        padding=15
                    ),
                    expand=True
                )
            ], spacing=0, expand=True),
            bgcolor=COLOR_BACKGROUND_PANEL,
            expand=3  # 30% of the row
        )
        
        # Main layout
        main_layout = ft.Row(
            [left_panel, right_panel],
            spacing=0,
            expand=True
        )
        
        self.page.add(main_layout)
        
        # Add welcome message to terminal
        self.add_terminal_line("=" * 60, COLOR_SUCCESS)
        self.add_terminal_line("  WELCOME TO NMAP DOJO - AI-POWERED TRAINING", COLOR_SUCCESS)
        self.add_terminal_line("=" * 60, COLOR_SUCCESS)
        self.add_terminal_line("")
        self.add_terminal_line("Type 'help' for available commands.", COLOR_TEXT_CYAN)
        self.add_terminal_line("Complete missions to earn XP and level up!", COLOR_TEXT_CYAN)
        self.add_terminal_line("")
    
    def initialize_api(self) -> None:
        """Initialize the Google Gemini API."""
        self.api_key = GEMINI_API_KEY
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(AI_MODEL)
            self.add_terminal_line("[+] AI Engine configured.", COLOR_SUCCESS)
            if self.api_key_banner:
                self.api_key_banner.visible = False
            self.page.update()
            self.generate_mission_async()
        except Exception as e:
            logger.error(f"API configuration failed: {e}")
            self.add_terminal_line(f"[!] API configuration failed: {e}", COLOR_ERROR)
            self.show_api_key_banner()
    
    def show_api_key_banner(self) -> None:
        """Show the API key input banner."""
        if self.api_key_banner:
            self.api_key_banner.visible = True
            self.add_terminal_line("[!] API key required. Please enter your key in the panel.", COLOR_TEXT_YELLOW)
            self.page.update()
    
    def on_api_key_submit(self, e: ft.ControlEvent) -> None:
        """Handle API key submission."""
        if self.api_key_input and self.api_key_input.value:
            self.api_key = self.api_key_input.value.strip()
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(AI_MODEL)
                if self.api_key_banner:
                    self.api_key_banner.visible = False
                self.add_terminal_line("[+] API key set! Generating mission...", COLOR_SUCCESS)
                self.page.update()
                self.generate_mission_async()
            except Exception as e:
                self.add_terminal_line(f"[!] API configuration error: {e}", COLOR_ERROR)
                self.page.update()
    
    def add_terminal_line(self, text: str, color: str = COLOR_TEXT_WHITE) -> None:
        """
        Add a line of text to the terminal output.
        
        Args:
            text: The text to display.
            color: The color of the text.
        """
        if self.terminal_output:
            self.terminal_output.controls.append(
                ft.Text(
                    text,
                    color=color,
                    font_family=FONT_MONOSPACE,
                    size=13,
                    selectable=True
                )
            )
            self.page.update()
    
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
    
    def generate_mission_async(self) -> None:
        """Generate a new mission asynchronously."""
        self.set_loading(True)
        self.mission_completed = False
        self.hints_used = 0
        self.update_hint_counter()
        
        if self.explain_btn:
            self.explain_btn.visible = False
        
        try:
            mission = self.generate_mission()
            if mission:
                self.current_mission = mission
                self.update_mission_display()
                self.add_terminal_line("")
                self.add_terminal_line(f"[NEW MISSION] {mission['title']}", COLOR_TEXT_CYAN)
                self.add_terminal_line(f"Target: {mission['target_ip']}", COLOR_TEXT_YELLOW)
                self.add_terminal_line("")
        except Exception as e:
            logger.error(f"Mission generation failed: {e}")
            self.add_terminal_line(f"[!] Mission generation failed: {str(e)}", COLOR_ERROR)
            self.add_terminal_line("[!] Click 'New Mission' to retry.", COLOR_TEXT_YELLOW)
        finally:
            self.set_loading(False)
    
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
                self.add_terminal_line("[!] Retrying mission generation...", COLOR_TEXT_YELLOW)
                time.sleep(3 * (retry + 1))
                return self.generate_mission(retry + 1)
            return None
        except Exception as e:
            logger.error(f"Mission generation error: {e}")
            if retry < 2:
                wait_time = 5 * (retry + 1)
                self.add_terminal_line(f"[!] AI Brain offline, retrying in {wait_time}s...", COLOR_TEXT_YELLOW)
                self.page.update()
                time.sleep(wait_time)
                return self.generate_mission(retry + 1)
            raise
    
    def update_mission_display(self) -> None:
        """Update the mission card UI with current mission data."""
        if not self.current_mission:
            return
        
        if self.mission_title:
            self.mission_title.value = self.current_mission['title']
        
        if self.mission_description:
            self.mission_description.value = self.current_mission['description']
        
        if self.mission_target:
            self.mission_target.value = f"Target: {self.current_mission['target_ip']}"
        
        if self.mission_difficulty:
            difficulty = self.current_mission.get('difficulty', 'Easy')
            colors = {
                'Easy': '#28a745',
                'Medium': '#ffc107',
                'Hard': '#fd7e14',
                'Expert': '#dc3545'
            }
            self.mission_difficulty.bgcolor = colors.get(difficulty, '#28a745')
            if self.mission_difficulty.content:
                self.mission_difficulty.content.value = difficulty
        
        self.page.update()
    
    def update_hint_counter(self) -> None:
        """Update the hint counter display."""
        if self.hint_counter:
            self.hint_counter.value = f"Hints Used: {self.hints_used}/{MAX_HINTS}"
            self.page.update()
    
    def set_loading(self, loading: bool) -> None:
        """
        Set the loading state of the UI.
        
        Args:
            loading: Whether to show loading state.
        """
        if self.loading_indicator:
            self.loading_indicator.visible = loading
        if self.command_input:
            self.command_input.disabled = loading
        if self.new_mission_btn:
            self.new_mission_btn.disabled = loading
        if self.get_hint_btn:
            self.get_hint_btn.disabled = loading
        self.page.update()
    
    def on_command_submit(self, e: ft.ControlEvent) -> None:
        """Handle command submission from the input field."""
        if not self.command_input:
            return
        
        command = self.command_input.value.strip() if self.command_input.value else ""
        
        if not command:
            self.add_terminal_line("[!] Command cannot be empty.", COLOR_ERROR)
            return
        
        # Add to command history
        if command and (not self.command_history or self.command_history[-1] != command):
            self.command_history.append(command)
            if len(self.command_history) > MAX_COMMAND_HISTORY:
                self.command_history.pop(0)
        self.history_index = len(self.command_history)
        
        # Clear input
        self.command_input.value = ""
        
        # Handle special commands
        if command.lower() == 'help':
            self.show_help()
            return
        elif command.lower() == 'clear':
            self.clear_terminal()
            return
        elif command.lower() == 'status':
            self.show_status()
            return
        
        # Display command
        self.add_terminal_line(f"> {command}", COLOR_TEXT_WHITE)
        
        # Validate if it's an nmap command
        if not command.startswith('nmap'):
            self.add_terminal_line("[!] Please enter a valid nmap command.", COLOR_ERROR)
            return
        
        if not self.current_mission:
            self.add_terminal_line("[!] No active mission. Click 'New Mission' to start.", COLOR_TEXT_YELLOW)
            return
        
        # Validate command with AI
        self.validate_command_async(command)
    
    def on_key_down(self, e: ft.KeyboardEvent) -> None:
        """Handle keyboard events for command history navigation."""
        if not self.command_input:
            return
        
        if e.key == "Arrow Up":
            # Navigate up in history
            if self.command_history and self.history_index > 0:
                self.history_index -= 1
                self.command_input.value = self.command_history[self.history_index]
                self.page.update()
        elif e.key == "Arrow Down":
            # Navigate down in history
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_input.value = self.command_history[self.history_index]
            else:
                self.history_index = len(self.command_history)
                self.command_input.value = ""
            self.page.update()
    
    def validate_command_async(self, command: str) -> None:
        """
        Validate the user's command asynchronously.
        
        Args:
            command: The nmap command to validate.
        """
        self.set_loading(True)
        self.add_terminal_line("[*] Scanning...", COLOR_TEXT_CYAN)
        
        try:
            result = self.validate_command(command)
            if result:
                self.process_validation_result(result, command)
        except Exception as e:
            logger.error(f"Validation error: {e}")
            self.add_terminal_line(f"[!] Validation error: {str(e)}", COLOR_ERROR)
            self.add_terminal_line("[!] Please try again.", COLOR_TEXT_YELLOW)
        finally:
            self.set_loading(False)
    
    def validate_command(self, command: str, retry: int = 0) -> Optional[ValidationResult]:
        """
        Validate the user's command using Gemini AI.
        
        Args:
            command: The nmap command to validate.
            retry: Number of retry attempts.
            
        Returns:
            ValidationResult dictionary or None if validation failed.
        """
        if not self.model or not self.current_mission:
            return None
        
        system_prompt = f"""You are a strict Nmap Exam Proctor. Analyze the user's command against the current scenario.

CURRENT MISSION:
- Title: {self.current_mission['title']}
- Description: {self.current_mission['description']}
- Target IP: {self.current_mission['target_ip']}
- Difficulty: {self.current_mission['difficulty']}
- Topic: {self.current_mission['topic_category']}

USER'S COMMAND: {command}

VALIDATION RULES:
- Be strict but educational
- If the command is 90% correct but missing a minor optimization, mark it correct but mention the improvement
- If the user uses deprecated flags (e.g., -P0 instead of -Pn), mark incorrect and explain the modern alternative
- For IPv6 scans, verify the user included the -6 flag
- For NSE script arguments, check proper --script-args syntax
- The simulated_output MUST look like real nmap output with proper formatting (Starting Nmap... Host is up... PORT STATE SERVICE...)
- Include NSE script output when applicable (3-5 lines minimum)

OUTPUT STRICT JSON FORMAT ONLY (no markdown, no code blocks):
{{"correct": true/false, "feedback": "Short explanation of the result", "simulated_output": "Realistic multi-line nmap terminal output"}}
"""
        
        try:
            logger.info(f"Validating command: {command}")
            response = self.model.generate_content(system_prompt)
            response_text = response.text.strip()
            
            # Clean up response
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            response_text = response_text.strip()
            
            logger.info(f"Validation response: {response_text}")
            
            result: ValidationResult = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in validation: {e}")
            if retry < 1:
                return self.validate_command(command, retry + 1)
            return None
        except Exception as e:
            logger.error(f"Validation error: {e}")
            if retry < 1:
                return self.validate_command(command, retry + 1)
            raise
    
    def process_validation_result(self, result: ValidationResult, command: str) -> None:
        """
        Process the validation result and update UI accordingly.
        
        Args:
            result: The validation result from AI.
            command: The original command.
        """
        if result.get('correct', False):
            # Success!
            self.add_terminal_line("")
            
            # Display simulated output
            simulated_output = result.get('simulated_output', '')
            for line in simulated_output.split('\n'):
                self.add_terminal_line(line, COLOR_SUCCESS)
            
            self.add_terminal_line("")
            self.add_terminal_line(f"[✓] {result.get('feedback', 'Correct!')}", COLOR_SUCCESS)
            
            # Award XP
            self.award_xp()
            self.mission_completed = True
            self.missions_completed += 1
            self.save_progress()
            
            self.add_terminal_line(f"[+] XP Awarded! Total: {self.xp}", COLOR_TEXT_CYAN)
            
            if self.explain_btn:
                self.explain_btn.visible = False
                
        else:
            # Failure
            self.add_terminal_line("")
            self.add_terminal_line(f"[✗] {result.get('feedback', 'Incorrect.')}", COLOR_ERROR)
            self.add_terminal_line("[!] Scan failed. Try again or get a hint.", COLOR_TEXT_YELLOW)
            
            if self.explain_btn:
                self.explain_btn.visible = True
        
        self.page.update()
    
    def award_xp(self) -> None:
        """Award XP based on hints used and check for level up."""
        old_level = self.level
        
        if self.hints_used == 0:
            xp_gained = XP_FIRST_TRY
        elif self.hints_used == 1:
            xp_gained = XP_ONE_HINT
        else:
            xp_gained = XP_TWO_HINTS
        
        self.xp += xp_gained
        self.level = self.calculate_level()
        
        # Update UI
        if self.xp_text:
            self.xp_text.value = f"XP: {self.xp}"
        if self.level_text:
            self.level_text.value = f"Level: {self.level}"
        
        # Check for level up
        if self.level > old_level:
            self.show_level_up_notification(old_level, self.level)
    
    def show_level_up_notification(self, old_level: int, new_level: int) -> None:
        """
        Display a level up notification.
        
        Args:
            old_level: Previous level.
            new_level: New level.
        """
        self.add_terminal_line("")
        self.add_terminal_line("=" * 50, COLOR_TEXT_YELLOW)
        self.add_terminal_line(f"  🎉 LEVEL UP! You are now Level {new_level}!", COLOR_TEXT_YELLOW)
        
        if new_level >= 4:
            self.add_terminal_line("  🔓 Advanced Red Team missions unlocked!", COLOR_SUCCESS)
        
        self.add_terminal_line("=" * 50, COLOR_TEXT_YELLOW)
        self.add_terminal_line("")
        
        # Show snackbar notification
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(
                f"🎉 LEVEL UP! You are now Level {new_level}!",
                color=COLOR_TEXT_WHITE,
                weight=ft.FontWeight.BOLD
            ),
            bgcolor=COLOR_SUCCESS
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def on_new_mission(self, e: ft.ControlEvent) -> None:
        """Handle New Mission button click."""
        self.generate_mission_async()
    
    def on_get_hint(self, e: ft.ControlEvent) -> None:
        """Handle Get Hint button click."""
        if not self.current_mission:
            self.add_terminal_line("[!] No active mission.", COLOR_TEXT_YELLOW)
            return
        
        if self.mission_completed:
            self.add_terminal_line("[!] Mission already completed. Start a new mission!", COLOR_TEXT_CYAN)
            return
        
        self.hints_used += 1
        self.update_hint_counter()
        
        if self.hints_used >= MAX_HINTS:
            # Show full answer
            self.get_full_answer()
        else:
            # Get a hint
            self.get_hint()
    
    def get_hint(self) -> None:
        """Get a hint for the current mission."""
        if not self.model or not self.current_mission:
            return
        
        self.set_loading(True)
        
        try:
            prompt = f"""Provide a helpful hint for this nmap scenario without giving the full answer:

Mission: {self.current_mission['title']}
Description: {self.current_mission['description']}
Target: {self.current_mission['target_ip']}
Topic: {self.current_mission['topic_category']}

Give ONE specific hint about which nmap flag or technique to use. Be helpful but don't reveal the full command."""

            response = self.model.generate_content(prompt)
            hint = response.text.strip()
            
            self.add_terminal_line("")
            self.add_terminal_line(f"[HINT] {hint}", COLOR_TEXT_YELLOW)
            self.add_terminal_line("")
            
        except Exception as e:
            logger.error(f"Hint generation error: {e}")
            self.add_terminal_line("[!] Could not generate hint. Try again.", COLOR_ERROR)
        finally:
            self.set_loading(False)
    
    def get_full_answer(self) -> None:
        """Get the full answer after using all hints."""
        if not self.model or not self.current_mission:
            return
        
        self.set_loading(True)
        
        try:
            prompt = f"""Provide the correct nmap command for this scenario:

Mission: {self.current_mission['title']}
Description: {self.current_mission['description']}
Target: {self.current_mission['target_ip']}
Topic: {self.current_mission['topic_category']}

Give the complete nmap command and briefly explain why each flag is used."""

            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            
            self.add_terminal_line("")
            self.add_terminal_line("[ANSWER REVEALED]", COLOR_TEXT_YELLOW)
            self.add_terminal_line(answer, COLOR_TEXT_CYAN)
            self.add_terminal_line("")
            self.add_terminal_line("[!] Try entering the command to complete the mission.", COLOR_TEXT_WHITE)
            
        except Exception as e:
            logger.error(f"Answer generation error: {e}")
            self.add_terminal_line("[!] Could not generate answer. Try again.", COLOR_ERROR)
        finally:
            self.set_loading(False)
    
    def on_explain_why(self, e: ft.ControlEvent) -> None:
        """Handle Explain Why button click."""
        if not self.model or not self.current_mission:
            return
        
        self.set_loading(True)
        
        try:
            prompt = f"""Explain why the user's last command was incorrect for this scenario:

Mission: {self.current_mission['title']}
Description: {self.current_mission['description']}
Target: {self.current_mission['target_ip']}
Topic: {self.current_mission['topic_category']}

Explain what was wrong and what the correct approach should be. Be educational and helpful."""

            response = self.model.generate_content(prompt)
            explanation = response.text.strip()
            
            self.add_terminal_line("")
            self.add_terminal_line("[EXPLANATION]", COLOR_TEXT_CYAN)
            for line in explanation.split('\n'):
                self.add_terminal_line(line, COLOR_TEXT_WHITE)
            self.add_terminal_line("")
            
        except Exception as e:
            logger.error(f"Explanation generation error: {e}")
            self.add_terminal_line("[!] Could not generate explanation. Try again.", COLOR_ERROR)
        finally:
            self.set_loading(False)
    
    def show_help(self) -> None:
        """Display help information."""
        self.add_terminal_line("")
        self.add_terminal_line("[HELP] Available Commands:", COLOR_TEXT_CYAN)
        self.add_terminal_line("  nmap [flags] [target] - Run an nmap command", COLOR_TEXT_WHITE)
        self.add_terminal_line("  help                  - Show this help message", COLOR_TEXT_WHITE)
        self.add_terminal_line("  clear                 - Clear the terminal", COLOR_TEXT_WHITE)
        self.add_terminal_line("  status                - Show current progress", COLOR_TEXT_WHITE)
        self.add_terminal_line("")
        self.add_terminal_line("[TIPS]", COLOR_TEXT_YELLOW)
        self.add_terminal_line("  - Use Up/Down arrows to navigate command history", COLOR_TEXT_WHITE)
        self.add_terminal_line("  - Click 'Get Hint' if you're stuck", COLOR_TEXT_WHITE)
        self.add_terminal_line("  - Complete missions to earn XP and level up!", COLOR_TEXT_WHITE)
        self.add_terminal_line("")
    
    def show_status(self) -> None:
        """Display current user status."""
        self.add_terminal_line("")
        self.add_terminal_line("[STATUS]", COLOR_TEXT_CYAN)
        self.add_terminal_line(f"  XP: {self.xp}", COLOR_SUCCESS)
        self.add_terminal_line(f"  Level: {self.level}", COLOR_SUCCESS)
        self.add_terminal_line(f"  Missions Completed: {self.missions_completed}", COLOR_TEXT_WHITE)
        
        # Show level progress
        if self.level < 5:
            min_xp, max_xp = LEVEL_THRESHOLDS[self.level]
            next_level_xp = LEVEL_THRESHOLDS[self.level + 1][0]
            self.add_terminal_line(f"  XP to next level: {next_level_xp - self.xp}", COLOR_TEXT_YELLOW)
        else:
            self.add_terminal_line("  Max level reached!", COLOR_SUCCESS)
        
        if self.level >= 4:
            self.add_terminal_line("  🔓 Advanced topics unlocked!", COLOR_TEXT_CYAN)
        
        self.add_terminal_line("")
    
    def clear_terminal(self) -> None:
        """Clear the terminal output."""
        if self.terminal_output:
            self.terminal_output.controls.clear()
            self.add_terminal_line("[*] Terminal cleared.", COLOR_TEXT_CYAN)


def main(page: ft.Page) -> None:
    """
    Main entry point for the Flet application.
    
    Args:
        page: The Flet page object.
    """
    app = NmapDojoApp(page)


if __name__ == "__main__":
    ft.app(target=main)
