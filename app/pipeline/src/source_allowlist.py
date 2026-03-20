from __future__ import annotations

from pathlib import Path


def parse_allowlist(md_path: str) -> list[dict[str, str]]:
    lines = Path(md_path).read_text(encoding="utf-8").splitlines()
    entries: list[dict[str, str]] = []
    current_name: str | None = None

    for line in lines:
        stripped = line.strip()
        if stripped and stripped[0].isdigit() and ". " in stripped and "Base URL:" not in stripped:
            current_name = stripped.split(". ", 1)[1].strip()
        if stripped.startswith("- Base URL:") and current_name:
            base_url = stripped.replace("- Base URL:", "").strip()
            entries.append({"name": current_name, "base_url": base_url})
            current_name = None

    return entries
