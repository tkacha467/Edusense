"""Prompt Manager and Repository for versioned prompt retrieval."""
from typing import Dict, Any, Optional
from app.ai.prompts.templates import PROMPT_TEMPLATES


class PromptManager:
    """Manages versioned prompt loading, variable substitution, and rendering."""

    def __init__(self) -> None:
        self.templates = PROMPT_TEMPLATES

    def render_prompt(
        self,
        prompt_key: str,
        variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Renders a versioned prompt template with key and variables.
        Returns dict with 'system', 'prompt', and 'version'.
        """
        template_info = self.templates.get(prompt_key)
        if not template_info:
            # Fallback for dynamic prompt key
            return {
                "system": "You are EduSense AI assistant.",
                "prompt": str(variables.get("query", "Provide guidance.")),
                "version": "1.0"
            }

        raw_template = template_info["template"]
        system_instruction = template_info.get("system", "")

        # Safely format variables using default blank fallback for missing keys
        formatted_prompt = raw_template
        for k, v in variables.items():
            formatted_prompt = formatted_prompt.replace(f"{{{k}}}", str(v))

        return {
            "system": system_instruction,
            "prompt": formatted_prompt,
            "version": template_info.get("version", "1.0")
        }
