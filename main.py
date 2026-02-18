#!/usr/bin/env python3
"""
Nmap Dojo - An AI-Powered Nmap Training Desktop Application

A robust, crash-proof desktop application using Python and Flet that trains
users on nmap commands. Uses Google Gemini 1.5 Pro as the game engine to
generate scenarios and validate answers.

Author: Nmap Dojo Team
"""

import flet as ft
from ui.app import NmapDojoApp


def main(page: ft.Page) -> None:
    """
    Main entry point for the Flet application.
    
    Args:
        page: The Flet page object.
    """
    app = NmapDojoApp(page)


if __name__ == "__main__":
    ft.app(target=main)
