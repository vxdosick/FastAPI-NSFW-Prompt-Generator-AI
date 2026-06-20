"""Build system prompts for general vs model-targeted generation."""

from core.config import SYSTEM_PROMPT
from core.model_guidelines import get_model_display_name, get_model_guidelines


def build_system_prompt(model_slug: str | None) -> str:
    if not model_slug:
        return SYSTEM_PROMPT

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"TARGET MODEL: {get_model_display_name(model_slug)}\n\n"
        "MODEL-SPECIFIC RULES (follow strictly for positive and negative prompts):\n"
        f"{get_model_guidelines(model_slug)}"
    )
