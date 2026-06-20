"""OpenRouter JSON schema for prompt generation responses."""

PROMPT_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "nsfw_prompt_generation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "boolean",
                    "description": (
                        "True if the user request is off-topic, unsafe, or cannot be turned into a valid prompt."
                    ),
                },
                "prompt": {
                    "type": "string",
                    "description": (
                        "Final English positive image prompt, ~500–700 characters. Pack dense visual detail. "
                        "Must be empty when error is true."
                    ),
                },
                "negative_prompt": {
                    "type": "string",
                    "description": (
                        "English negative prompt tailored to the target model/workflow. Include artifact and "
                        "quality exclusions when the model benefits from negatives; use a short minimal negative "
                        "or empty string when negatives are optional. Must be empty when error is true."
                    ),
                },
                "title": {
                    "type": "string",
                    "description": (
                        "2–3 short English words labeling the scene for the user's saved list. "
                        "Must be empty when error is true."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": (
                        "Short machine-oriented tag or note when error is true (e.g. off_topic, minors, "
                        "not_a_prompt_request). Empty string when error is false."
                    ),
                },
            },
            "required": ["error", "prompt", "negative_prompt", "title", "reason"],
            "additionalProperties": False,
        },
    },
}
