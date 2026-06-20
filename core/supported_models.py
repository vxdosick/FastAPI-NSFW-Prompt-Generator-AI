"""Canonical display list — same models as MODEL_REGISTRY, popularity order."""

from core.model_guidelines import MODEL_COMMAND_SLUGS, MODEL_REGISTRY

OTHER_MODELS_SUFFIX = "and other NSFW models"

SUPPORTED_MODELS = [
    MODEL_REGISTRY[slug]["display_name"] for slug in MODEL_COMMAND_SLUGS
]


def supported_models_phrase() -> str:
    return f"{', '.join(SUPPORTED_MODELS)}, {OTHER_MODELS_SUFFIX}"
