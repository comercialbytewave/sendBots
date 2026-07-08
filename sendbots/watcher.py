from __future__ import annotations

import logging
from pathlib import Path

from sendbots.models import FileGroup, ParsedFile
from sendbots.parser import is_marked_sent, is_pdf, parse_file
from sendbots.renamer import archive_marked_sent


LOGGER = logging.getLogger(__name__)


def is_file_stable(path: Path) -> bool:
    try:
        first = path.stat().st_size
        with path.open("ab"):
            pass
        second = path.stat().st_size
    except OSError:
        return False
    return first == second and first > 0


def scan_folder(folder: Path) -> tuple[list[FileGroup], list[Path], list[Path]]:
    groups_by_number: dict[str, FileGroup] = {}
    invalid: list[Path] = []
    skipped_sent: list[Path] = []

    if not folder.exists() or not folder.is_dir():
        return [], invalid, skipped_sent

    for path in sorted(folder.iterdir()):
        if not path.is_file() or not is_pdf(path):
            continue
        if is_marked_sent(path):
            try:
                archive_marked_sent(path)
            except OSError:
                LOGGER.exception("Falha ao mover arquivo enviado para a pasta Enviados: %s", path)
                skipped_sent.append(path)
            continue
        parsed = parse_file(path)
        if parsed is None:
            invalid.append(path)
            continue
        if not is_file_stable(path):
            continue
        group = groups_by_number.setdefault(parsed.whatsapp, FileGroup(parsed.whatsapp))
        _append_parsed(group, parsed)

    return list(groups_by_number.values()), invalid, skipped_sent


def _append_parsed(group: FileGroup, parsed: ParsedFile) -> None:
    if parsed.kind == "note":
        group.notes.append(parsed)
    else:
        group.boletos.append(parsed)
