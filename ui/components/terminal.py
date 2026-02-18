"""
Terminal UI component for Nmap Dojo.
"""

import flet as ft
from config.constants import (
    COLOR_BACKGROUND_TERMINAL,
    COLOR_BACKGROUND_PANEL,
    COLOR_SUCCESS,
    COLOR_TEXT_CYAN,
    FONT_MONOSPACE
)


def create_terminal_panel(terminal_output: ft.ListView, command_input: ft.TextField, loading_indicator: ft.ProgressRing) -> ft.Container:
    """
    Create the terminal panel (left side of UI).
    
    Args:
        terminal_output: The ListView for terminal output.
        command_input: The TextField for command input.
        loading_indicator: The ProgressRing for loading state.
    
    Returns:
        Container with the terminal panel layout.
    """
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
                content=terminal_output,
                expand=True,
                bgcolor=COLOR_BACKGROUND_TERMINAL,
                padding=5
            ),
            ft.Container(
                content=ft.Row([
                    command_input,
                    loading_indicator
                ]),
                padding=10,
                bgcolor=COLOR_BACKGROUND_PANEL
            )
        ], spacing=0, expand=True),
        bgcolor=COLOR_BACKGROUND_TERMINAL,
        expand=7  # 70% of the row
    )
    
    return left_panel
