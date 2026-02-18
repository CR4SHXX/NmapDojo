"""
Command validation for Nmap Dojo.
"""

import json
import re
from typing import Optional
from models.types import ValidationResult, MissionData
from utils.logger import logger


class CommandValidator:
    """Validates user commands against mission requirements using AI."""
    
    def __init__(self, model):
        """
        Initialize the command validator.
        
        Args:
            model: The AI model instance.
        """
        self.model = model
    
    def validate_command(self, command: str, current_mission: MissionData, retry: int = 0) -> Optional[ValidationResult]:
        """
        Validate the user's command using Gemini AI.
        
        Args:
            command: The nmap command to validate.
            current_mission: The current mission data.
            retry: Number of retry attempts.
            
        Returns:
            ValidationResult dictionary or None if validation failed.
        """
        if not self.model or not current_mission:
            return None
        
        system_prompt = f"""You are a strict Nmap Exam Proctor. Analyze the user's command against the current scenario.

CURRENT MISSION:
- Title: {current_mission['title']}
- Description: {current_mission['description']}
- Target IP: {current_mission['target_ip']}
- Difficulty: {current_mission['difficulty']}
- Topic: {current_mission['topic_category']}

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
                return self.validate_command(command, current_mission, retry + 1)
            return None
        except Exception as e:
            logger.error(f"Validation error: {e}")
            if retry < 1:
                return self.validate_command(command, current_mission, retry + 1)
            raise
    
    def process_validation_result(self, result: ValidationResult, command: str, callbacks: dict) -> None:
        """
        Process the validation result and trigger appropriate callbacks.
        
        Args:
            result: The validation result from AI.
            command: The original command.
            callbacks: Dictionary of callback functions:
                - add_terminal_line: function to add output lines
                - award_xp: function to award XP
                - save_progress: function to save progress
                - update_page: function to update UI
                - set_mission_completed: function to mark mission as completed
                - update_missions_completed: function to increment missions count
                - set_explain_visible: function to show/hide explain button
        """
        add_terminal_line = callbacks.get('add_terminal_line')
        award_xp = callbacks.get('award_xp')
        save_progress = callbacks.get('save_progress')
        update_page = callbacks.get('update_page')
        set_mission_completed = callbacks.get('set_mission_completed')
        update_missions_completed = callbacks.get('update_missions_completed')
        set_explain_visible = callbacks.get('set_explain_visible')
        
        if result.get('correct', False):
            # Success!
            add_terminal_line("")
            
            # Display simulated output
            simulated_output = result.get('simulated_output', '')
            from config.constants import COLOR_SUCCESS
            for line in simulated_output.split('\n'):
                add_terminal_line(line, COLOR_SUCCESS)
            
            add_terminal_line("")
            add_terminal_line(f"[✓] {result.get('feedback', 'Correct!')}", COLOR_SUCCESS)
            
            # Award XP
            xp_total = award_xp()
            set_mission_completed(True)
            update_missions_completed()
            save_progress()
            
            from config.constants import COLOR_TEXT_CYAN
            add_terminal_line(f"[+] XP Awarded! Total: {xp_total}", COLOR_TEXT_CYAN)
            
            set_explain_visible(False)
                
        else:
            # Failure
            from config.constants import COLOR_ERROR, COLOR_TEXT_YELLOW
            add_terminal_line("")
            add_terminal_line(f"[✗] {result.get('feedback', 'Incorrect.')}", COLOR_ERROR)
            add_terminal_line("[!] Scan failed. Try again or get a hint.", COLOR_TEXT_YELLOW)
            
            set_explain_visible(True)
        
        update_page()
