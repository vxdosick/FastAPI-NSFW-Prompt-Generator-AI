"""Per-model prompt engineering rules for targeted generation commands."""

from __future__ import annotations

MODEL_REGISTRY: dict[str, dict[str, str]] = {
    "ponyxl": {
        "display_name": "Pony XL",
        "guidelines": (
            "Pony XL requires specific score quality tags at the very beginning of the positive prompt "
            "for optimal quality: score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up. "
            "Use source_pony, source_furry, source_anime, or source_cartoon to steer style, and "
            "rating_explicit / rating_questionable for NSFW control. The model responds strongly to a mix "
            "of natural language descriptions and Danbooru-style tags; negative prompts are often minimal "
            "or unnecessary, but explicitly exclude low-score tags (score_6, score_5) when aiming for "
            "high quality."
        ),
    },
    "ponydiffusion": {
        "display_name": "Pony Diffusion",
        "guidelines": (
            "Pony Diffusion requires specific score quality tags at the very beginning of the positive "
            "prompt for optimal quality: score_9, score_8_up, score_7_up, score_6_up, score_5_up, "
            "score_4_up. Use source_pony, source_furry, source_anime, or source_cartoon to steer style, "
            "and rating_explicit / rating_questionable for NSFW control. The model responds strongly to a "
            "mix of natural language descriptions and Danbooru-style tags; negative prompts are often "
            "minimal or unnecessary, but explicitly exclude low-score tags (score_6, score_5) when aiming "
            "for high quality."
        ),
    },
    "fluxedup": {
        "display_name": "Fluxed Up",
        "guidelines": (
            "Fluxed Up excels with detailed natural language prompts rather than heavy comma-separated tags. "
            "Describe subjects, actions, lighting, anatomy, and explicit elements in full sentences for best "
            "coherence and detail. It benefits from photography or cinematic descriptors (e.g., soft natural "
            "window light, detailed skin texture with pores) and responds well to explicit NSFW terminology "
            "without strong censorship. Use recommended samplers like DPM++ 2M with Beta scheduler; keep "
            "negative prompts light or focused on artifacts."
        ),
    },
    "illustrious": {
        "display_name": "Illustrious",
        "guidelines": (
            "Illustrious works best with a combination of Danbooru-style tags and natural language "
            "descriptions. Include quality boosters such as masterpiece, best quality, highly detailed and "
            "specific lighting/anatomy terms (e.g., volumetric lighting, subsurface scattering, detailed skin "
            "texture). It handles both anime and semi-realistic styles effectively; use rating or style tags "
            "when needed and emphasize expressive faces or complex compositions for stronger results."
        ),
    },
    "automatic1111": {
        "display_name": "Automatic1111",
        "guidelines": (
            "Automatic1111 uses standard Stable Diffusion prompting with support for parentheses weighting "
            "(term:1.2) and negative prompts. Start with subject + action + environment + style + lighting, "
            "then add technical details; negative prompts are crucial for removing deformities, artifacts, and "
            "unwanted elements. It is highly flexible and benefits from detailed, structured prompts with "
            "photography or artistic terms depending on the loaded checkpoint."
        ),
    },
    "comfyui": {
        "display_name": "ComfyUI",
        "guidelines": (
            "ComfyUI follows core Stable Diffusion prompting rules but offers maximum flexibility through "
            "custom workflows and nodes. Use natural language mixed with tags/keywords, parentheses weighting, "
            "and strong negative prompts; the effectiveness depends heavily on the loaded model and "
            "sampler/scheduler nodes. It excels with precise control over prompt structure, allowing layered "
            "or conditional prompting for complex scenes."
        ),
    },
    "fooocus": {
        "display_name": "Fooocus",
        "guidelines": (
            "Fooocus is designed for simplicity and performs best with straightforward natural language prompts. "
            "It automatically expands and enhances prompts internally, so detailed but concise descriptions of "
            "subject, pose, lighting, and style work very well without heavy engineering. Minimal negative "
            "prompting is usually sufficient; it handles both realistic and stylized content effectively with "
            "little manual optimization."
        ),
    },
    "forge": {
        "display_name": "Forge",
        "guidelines": (
            "Forge behaves similarly to Automatic1111 with full support for weighted prompts, negative prompts, "
            "and standard SDXL/Flux syntax. Use structured prompts (subject + details + lighting + technical "
            "terms) and leverage its optimized performance for higher step counts or complex models. It benefits "
            "from the same photography-focused or tag-based approaches as the underlying checkpoint, with excellent "
            "handling of Flux and SDXL fine-tunes."
        ),
    },
    "realvisxl": {
        "display_name": "RealVisXL",
        "guidelines": (
            "RealVisXL is optimized for photorealism and responds strongly to photography terminology such as "
            "shot on Canon EOS R5, 85mm f/1.4 lens, shallow depth of field, natural skin texture with visible "
            "pores. Use detailed natural language or keyword lists describing lighting (cinematic, soft window "
            "light), camera settings, and anatomy; negative prompts targeting deformities and over-smoothing are "
            "important. Avoid overly artistic or anime tags unless intentionally mixing styles."
        ),
    },
    "juggernautxl": {
        "display_name": "Juggernaut XL",
        "guidelines": (
            "Juggernaut XL excels with photography-style prompting — include camera models, lenses, lighting setups "
            "(golden hour, cinematic lighting), and technical details like highly detailed skin texture, sharp focus, "
            "bokeh. Structured prompts combining subject description with environment, mood, and professional "
            "photography terms produce the most realistic results. Negative prompts should target artifacts, "
            "deformities, and text/watermarks for clean outputs."
        ),
    },
    "cyberrealistic": {
        "display_name": "CyberRealistic",
        "guidelines": (
            "CyberRealistic performs well with relatively simple yet descriptive prompts focused on photorealism. "
            "Emphasize natural lighting, skin details (pores, texture, sheen), depth of field, and cinematic or "
            "editorial photography terms. It handles both minimal and detailed prompts effectively; include explicit "
            "anatomical descriptions for NSFW work and use negative prompts to refine skin and anatomy quality."
        ),
    },
    "noobaixl": {
        "display_name": "NoobAI-XL",
        "guidelines": (
            "NoobAI-XL (built on Illustrious) works best with Danbooru tags combined with natural language. "
            "Include quality enhancers like masterpiece, best quality, highly detailed and specific descriptors "
            "for anatomy, lighting, and expression. It excels at anime and semi-realistic styles with strong prompt "
            "adherence; use rating tags for NSFW control and emphasize complex compositions or character details "
            "for superior results."
        ),
    },
    "grok2": {
        "display_name": "Grok-2",
        "guidelines": (
            "Grok-2 (Flux-based) performs best with clear, detailed natural language prompts describing the full "
            "scene, subjects, actions, lighting, and mood in sentence form. It handles complex compositions and "
            "explicit content well with minimal tag reliance. Focus on visual storytelling and specific descriptors "
            "(anatomy, textures, atmosphere) rather than heavy keyword stacking; negative prompts are generally less "
            "critical than in SDXL models."
        ),
    },
    "persephone": {
        "display_name": "Persephone",
        "guidelines": (
            "Persephone (Flux NSFW/SFW checkpoint) responds excellently to detailed natural language descriptions "
            "similar to other Flux fine-tunes. Describe subjects, explicit elements, lighting, and environment in full "
            "sentences for coherent, high-quality results. It balances SFW and NSFW output effectively and benefits "
            "from photography/cinematic terms and precise anatomical details. Use recommended Flux settings "
            "(e.g., DPM++ 2M + Beta) for optimal prompt following."
        ),
    },
}

MODEL_COMMAND_SLUGS: tuple[str, ...] = tuple(MODEL_REGISTRY.keys())


def resolve_command_slug(command: str) -> str | None:
    slug = (command or "").strip().lower()
    if "@" in slug:
        slug = slug.split("@", 1)[0]
    return slug if slug in MODEL_REGISTRY else None


def get_model_display_name(slug: str) -> str:
    return MODEL_REGISTRY[slug]["display_name"]


def get_model_guidelines(slug: str) -> str:
    return MODEL_REGISTRY[slug]["guidelines"]


def models_help_lines() -> list[str]:
    lines = []
    for slug in MODEL_COMMAND_SLUGS:
        name = MODEL_REGISTRY[slug]["display_name"]
        lines.append(f"/{slug} — {name}")
    return lines
