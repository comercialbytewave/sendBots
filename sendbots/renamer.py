from __future__ import annotations

from pathlib import Path


def sent_name_for(path: Path) -> Path:
    target = path.with_name(f"{path.stem}_ENV{path.suffix}")
    if not target.exists():
        return target

    index = 1
    while True:
        candidate = path.with_name(f"{path.stem}_ENV_{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def mark_as_sent(path: Path) -> Path:
    target = sent_name_for(path)
    path.rename(target)
    return target

