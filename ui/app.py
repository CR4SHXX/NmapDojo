"""
Main application class for Nmap Dojo.
"""

import flet as ft
from typing import Optional, List
from pathlib import Path

from config.constants import (
    COLOR_BACKGROUND_TERMINAL,
    COLOR_BACKGROUND_PANEL,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_YELLOW,
    COLOR_TEXT_CYAN,
    FONT_MONOSPACE,
    XP_FIRST_TRY,
    XP_ONE_HINT,
    XP_TWO_HINTS,
    LEVEL_THRESHOLDS,
    MAX_HINTS,
    MAX_COMMAND_HISTORY
)
from config.settings import GEMINI_API_KEY
from models.types import MissionData, ValidationResult, ProgressData
from core import ProgressManager, MissionGenerator, CommandValidator, AIService
from ui.components import create_terminal_panel, create_mission_panel, get_difficulty_badge_color
from utils.logger import logger


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
        
        # Initialize services
        self.ai_service = AIService()
        self.progress_manager = ProgressManager()
        self.command_validator: Optional[CommandValidator] = None
        self.mission_generator: Optional[MissionGenerator] = None
        
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
        data = self.progress_manager.load_progress()
        self.xp = data['xp']
        self.level = data['level']
        self.last_topic_index = data['last_topic_index']
        self.missions_completed = data['missions_completed']
    
    def save_progress(self) -> None:
        """Save user progress to the JSON file."""
        data: ProgressData = {
            'xp': self.xp,
            'level': self.level,
            'last_topic_index': self.last_topic_index,
            'missions_completed': self.missions_completed
        }
        self.progress_manager.save_progress(data)
    
    def calculate_level(self) -> int:
        """
        Calculate the current level based on XP.
        
        Returns:
            The calculated level (1-5).
        """
        return self.progress_manager.calculate_level(self.xp)
    
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
        
        # Create panels using component functions
        left_panel = create_terminal_panel(self.terminal_output, self.command_input, self.loading_indicator)
        right_panel = create_mission_panel(
            self.xp_text,
            self.level_text,
            self.mission_title,
            self.mission_description,
            self.mission_target,
            self.mission_difficulty,
            self.hint_counter,
            self.new_mission_btn,
            self.get_hint_btn,
            self.explain_btn,
            self.api_key_banner
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
        success = self.ai_service.initialize_api()
        if success:
            self.command_validator = CommandValidator(self.ai_service.model)
            self.mission_generator = MissionGenerator(
                self.ai_service.model,
                self.level,
                self.last_topic_index
            )
            self.add_terminal_line("[+] AI Engine configured.", COLOR_SUCCESS)
            if self.api_key_banner:
                self.api_key_banner.visible = False
            self.page.update()
            self.generate_mission_async()
        else:
            self.add_terminal_line(f"[!] API configuration failed.", COLOR_ERROR)
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
            api_key = self.api_key_input.value.strip()
            success = self.ai_service.initialize_api(api_key)
            if success:
                self.command_validator = CommandValidator(self.ai_service.model)
                self.mission_generator = MissionGenerator(
                    self.ai_service.model,
                    self.level,
                    self.last_topic_index
                )
                if self.api_key_banner:
                    self.api_key_banner.visible = False
                self.add_terminal_line("[+] API key set! Generating mission...", COLOR_SUCCESS)
                self.page.update()
                self.generate_mission_async()
            else:
                self.add_terminal_line(f"[!] API configuration error.", COLOR_ERROR)
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
    
    def generate_mission_async(self) -> None:
        """Generate a new mission asynchronously."""
        self.set_loading(True)
        self.mission_completed = False
        self.hints_used = 0
        self.update_hint_counter()
        
        if self.explain_btn:
            self.explain_btn.visible = False
        
        self.add_terminal_line("[*] Generating new mission...", COLOR_TEXT_CYAN)
        
        def _run() -> None:
            try:
                # Update mission generator with current state
                if self.mission_generator:
                    self.mission_generator.level = self.level
                    self.mission_generator.last_topic_index = self.last_topic_index
                    
                    mission = self.mission_generator.generate_mission()
                    if mission:
                        self.current_mission = mission
                        self.last_topic_index = self.mission_generator.last_topic_index
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
        
        self.page.run_thread(_run)
    
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
            self.mission_difficulty.bgcolor = get_difficulty_badge_color(difficulty)
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
        if self.explain_btn:
            self.explain_btn.disabled = loading
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
        
        def _run() -> None:
            try:
                if self.command_validator and self.current_mission:
                    result = self.command_validator.validate_command(command, self.current_mission)
                    if result:
                        self.process_validation_result(result, command)
            except Exception as e:
                logger.error(f"Validation error: {e}")
                self.add_terminal_line(f"[!] Validation error: {str(e)}", COLOR_ERROR)
                self.add_terminal_line("[!] Please try again.", COLOR_TEXT_YELLOW)
            finally:
                self.set_loading(False)
        
        self.page.run_thread(_run)
    
    def process_validation_result(self, result: ValidationResult, command: str) -> None:
        """
        Process the validation result and update UI accordingly.
        
        Args:
            result: The validation result from AI.
            command: The original command.
        """
        # Create callbacks for the validator
        callbacks = {
            'add_terminal_line': self.add_terminal_line,
            'award_xp': self.award_xp,
            'save_progress': self.save_progress,
            'update_page': lambda: self.page.update(),
            'set_mission_completed': lambda completed: setattr(self, 'mission_completed', completed),
            'update_missions_completed': lambda: setattr(self, 'missions_completed', self.missions_completed + 1),
            'set_explain_visible': lambda visible: setattr(self.explain_btn, 'visible', visible) if self.explain_btn else None
        }
        
        self.command_validator.process_validation_result(result, command, callbacks)
    
    def award_xp(self) -> int:
        """
        Award XP based on hints used and check for level up.
        
        Returns:
            The new total XP.
        """
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
        
        return self.xp
    
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
        if not self.current_mission:
            return
        
        self.set_loading(True)
        self.add_terminal_line("[*] Getting hint...", COLOR_TEXT_CYAN)
        
        def _run() -> None:
            try:
                hint = self.ai_service.get_hint(self.current_mission)
                
                self.add_terminal_line("")
                self.add_terminal_line(f"[HINT] {hint}", COLOR_TEXT_YELLOW)
                self.add_terminal_line("")
                
            except Exception as e:
                logger.error(f"Hint generation error: {e}")
                self.add_terminal_line("[!] Could not generate hint. Try again.", COLOR_ERROR)
            finally:
                self.set_loading(False)
        
        self.page.run_thread(_run)
    
    def get_full_answer(self) -> None:
        """Get the full answer after using all hints."""
        if not self.current_mission:
            return
        
        self.set_loading(True)
        self.add_terminal_line("[*] Generating answer...", COLOR_TEXT_CYAN)
        
        def _run() -> None:
            try:
                answer = self.ai_service.get_full_answer(self.current_mission)
                
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
        
        self.page.run_thread(_run)
    
    def on_explain_why(self, e: ft.ControlEvent) -> None:
        """Handle Explain Why button click."""
        if not self.current_mission:
            return
        
        self.set_loading(True)
        self.add_terminal_line("[*] Generating explanation...", COLOR_TEXT_CYAN)
        
        def _run() -> None:
            try:
                explanation = self.ai_service.get_explanation(self.current_mission)
                
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
        
        self.page.run_thread(_run)
    
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
