"""Canonical list of supported image-generation tools and model families."""

# Ordered by popularity (descending).
SUPPORTED_MODELS = [
    "Pony XL",
    "Fluxed Up",
    "Pony Diffusion",
    "Illustrious",
    "Automatic1111",
    "ComfyUI",
    "Fooocus",
    "Forge",
    "RealVisXL",
    "Juggernaut XL",
    "CyberRealistic",
    "NoobAI-XL",
    "Grok-2",
    "Persephone",
]

OTHER_MODELS_SUFFIX = "and other NSFW models"


def supported_models_phrase() -> str:
    return f"{', '.join(SUPPORTED_MODELS)}, {OTHER_MODELS_SUFFIX}"
