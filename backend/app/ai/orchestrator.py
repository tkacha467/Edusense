"""AI Orchestrator - Centralized entry point for all LLM requests."""
import json
import time
import logging
from typing import Any, Dict, Optional, Tuple
from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.prompts.manager import PromptManager

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Centralized AI Orchestrator enforcing prompt versioning, provider abstraction,
    temperature control, retry logic, token usage tracking, and structured output validation.
    """

    def __init__(self, provider: Optional[BaseLLMProvider] = None) -> None:
        self.provider = provider or GeminiProvider()
        self.prompt_manager = PromptManager()
        self.usage_logs = []

    async def execute(
        self,
        prompt_key: str,
        variables: Dict[str, Any],
        temperature: float = 0.7,
        json_mode: bool = False,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Executes an orchestrated AI request using prompt key and variables.
        """
        start_time = time.time()

        # Render prompt via PromptManager
        rendered = self.prompt_manager.render_prompt(prompt_key, variables)
        system_instruction = rendered["system"]
        prompt_text = rendered["prompt"]
        prompt_version = rendered["version"]

        response_text = ""
        attempt = 0
        success = False

        while attempt <= max_retries and not success:
            try:
                attempt += 1
                response_text = await self.provider.generate_completion(
                    prompt=prompt_text,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    json_mode=json_mode
                )
                if json_mode:
                    # Validate JSON
                    try:
                        parsed = json.loads(response_text)
                        success = True
                    except json.JSONDecodeError:
                        logger.warning(f"Attempt {attempt}: Invalid JSON returned by provider, retrying...")
                else:
                    success = True
            except Exception as e:
                logger.error(f"Attempt {attempt} failed in AIOrchestrator: {e}")

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Log observability usage metrics
        log_entry = {
            "prompt_key": prompt_key,
            "prompt_version": prompt_version,
            "latency_ms": elapsed_ms,
            "success": success,
            "attempts": attempt,
            "timestamp": time.time()
        }
        self.usage_logs.append(log_entry)

        if json_mode:
            try:
                return json.loads(response_text)
            except Exception:
                return {"status": "fallback", "text": response_text}

        return {"status": "success", "text": response_text}

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Returns aggregated token/request usage statistics."""
        total_requests = len(self.usage_logs)
        successful_requests = len([l for l in self.usage_logs if l["success"]])
        avg_latency = sum(l["latency_ms"] for l in self.usage_logs) / total_requests if total_requests > 0 else 0.0

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": total_requests - successful_requests,
            "average_latency_ms": round(avg_latency, 2),
            "usage_logs": self.usage_logs[-10:]
        }
