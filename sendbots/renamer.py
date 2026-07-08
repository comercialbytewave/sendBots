from __future__ import annotations

from pathlib import Path

from sendbots.parser import is_marked_sent


SENT_FOLDER_NAME = "Enviados"


def sent_folder_for(path: Path) -> Path:
    return path.parent / SENT_FOLDER_NAME


def sent_name_for(path: Path) -> Path:
    target = sent_folder_for(path) / f"{path.stem}_ENV{path.suffix}"
    if not target.exists():
        return target

    index = 1
    while True:
        candidate = target.with_name(f"{path.stem}_ENV_{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def mark_as_sent(path: Path) -> Path:
    target = sent_name_for(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    path.rename(target)
    return target


def archive_marked_sent(path: Path) -> Path:
    """Move um arquivo _ENV antigo da pasta monitorada para Enviados."""
    if not is_marked_sent(path):
        raise ValueError(f"Arquivo nao esta marcado como enviado: {path}")

    folder = sent_folder_for(path)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / path.name
    index = 1
    while target.exists():
        target = folder / f"{path.stem}_{index}{path.suffix}"
        index += 1
    path.rename(target)
    return target
