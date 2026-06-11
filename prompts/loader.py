from config import config


def load_prompt(
    prompt_name: str,
    version: str = "current",
) -> str:
    path = config.PROMPT_PATH / prompt_name / f"{version}.md"

    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")

    return path.read_text(encoding="utf-8")
