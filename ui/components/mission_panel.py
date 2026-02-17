"""
Mission panel UI component for Nmap Dojo.
"""

import flet as ft
from config.constants import (
    COLOR_BACKGROUND_PANEL,
    COLOR_BACKGROUND_TERMINAL,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_YELLOW,
    COLOR_TEXT_CYAN,
    MAX_HINTS
)


def create_mission_panel(
    xp_text: ft.Text,
    level_text: ft.Text,
    mission_title: ft.Text,
    mission_description: ft.Text,
    mission_target: ft.Text,
    mission_difficulty: ft.Container,
    hint_counter: ft.Text,
    new_mission_btn: ft.ElevatedButton,
    get_hint_btn: ft.ElevatedButton,
    explain_btn: ft.ElevatedButton,
    api_key_banner: ft.Container
) -> ft.Container:
    """
    Create the mission panel (right side of UI).
    
    Args:
        xp_text: Text control for XP display.
        level_text: Text control for level display.
        mission_title: Text control for mission title.
        mission_description: Text control for mission description.
        mission_target: Text control for target IP.
        mission_difficulty: Container for difficulty badge.
        hint_counter: Text control for hints counter.
        new_mission_btn: Button for new mission.
        get_hint_btn: Button for getting hints.
        explain_btn: Button for explanation.
        api_key_banner: Container for API key input.
    
    Returns:
        Container with the mission panel layout.
    """
    # Stats bar
    stats_bar = ft.Row(
        [xp_text, level_text],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    
    # Mission card container
    mission_card = ft.Container(
        content=ft.Column([
            mission_title,
            ft.Divider(color=COLOR_TEXT_WHITE, height=1),
            mission_description,
            ft.Row([mission_target, mission_difficulty], 
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            hint_counter
        ], spacing=10),
        bgcolor="#1f2937",
        padding=15,
        border_radius=10,
        margin=ft.margin.only(bottom=10)
    )
    
    # Action buttons
    buttons_row = ft.Row(
        [new_mission_btn, get_hint_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        wrap=True
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
                        explain_btn,
                        api_key_banner
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
    
    return right_panel
